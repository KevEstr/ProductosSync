"""
Programador de tareas para sincronización automática
"""
import os
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from src.config import Config
from src.logger import setup_logger
from src.cache_manager import cache_manager
from src.cloudflare_uploader import cloudflare_uploader

logger = setup_logger(__name__)


class TaskScheduler:
    """Gestor de tareas programadas"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.dbf_reader = None
        self.last_modification_times = {}
    
    def set_dbf_reader(self, dbf_reader):
        self.dbf_reader = dbf_reader
    
    def _check_files_modified(self) -> bool:
        try:
            if self.dbf_reader is None:
                return False

            dbf_path = Path(self.dbf_reader.dbf_path)
            mes_actual = datetime.now().month
            files_to_check = ['Producto.DBF', 'MovMes.DBF', f'MovMes{mes_actual:02d}.DBF']
            has_changes = False

            for filename in files_to_check:
                filepath = dbf_path / filename
                if not filepath.exists():
                    continue
                current_mtime = os.path.getmtime(filepath)
                if filename not in self.last_modification_times:
                    self.last_modification_times[filename] = current_mtime
                    has_changes = True
                elif current_mtime > self.last_modification_times[filename]:
                    logger.info(f"Cambios detectados en {filename}")
                    self.last_modification_times[filename] = current_mtime
                    has_changes = True

            return has_changes

        except Exception as e:
            logger.error(f"Error verificando archivos: {e}")
            return True
    
    def sync_cache(self):
        """Sincroniza el caché local (cada 30 minutos)"""
        try:
            if self.dbf_reader is None:
                return

            cache_missing = cache_manager.get('inventario_completo') is None
            if not (self._check_files_modified() or cache_missing):
                return

            inicio = datetime.now()
            inventario = self.dbf_reader.get_inventario_con_precios()
            cache_manager.set('inventario_completo', inventario)
            
            # Solo invalidar otros cachés si la actualización fue exitosa
            cache_manager.invalidate('productos_True')
            cache_manager.invalidate('productos_False')
            cache_manager.invalidate('precios')

            logger.info(f"Cache local actualizado: {len(inventario)} productos en {(datetime.now() - inicio).total_seconds():.2f}s")

        except Exception as e:
            logger.error(f"Error en sincronizacion de cache: {e}")
            logger.info("Manteniendo caché anterior debido al error")
    
    def sync_cloudflare(self):
        """Sincroniza con Cloudflare R2 (3 veces al día: 6 AM, 12 PM, 6 PM)"""
        try:
            if self.dbf_reader is None:
                logger.warning("DBF Reader no inicializado, omitiendo subida a Cloudflare")
                return
            
            if not Config.CLOUDFLARE_ENABLED:
                logger.debug("Cloudflare deshabilitado, omitiendo subida")
                return
            
            logger.info("=" * 80)
            logger.info(f"INICIANDO SINCRONIZACION CON CLOUDFLARE R2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            
            inicio = datetime.now()
            
            # Obtener datos actualizados
            inventario = self.dbf_reader.get_inventario_con_precios()
            productos = self.dbf_reader.get_productos(activos_solo=True)
            precios = self.dbf_reader.get_precios()
            
            # Subir a Cloudflare R2
            success_count = 0
            
            if cloudflare_uploader.upload_inventario(inventario):
                success_count += 1
            
            if cloudflare_uploader.upload_productos(productos):
                success_count += 1
            
            if cloudflare_uploader.upload_precios(precios):
                success_count += 1
            
            tiempo_total = (datetime.now() - inicio).total_seconds()
            
            if success_count == 3:
                logger.info(f"SINCRONIZACION EXITOSA: {success_count}/3 archivos subidos en {tiempo_total:.2f}s")
            else:
                logger.warning(f"SINCRONIZACION PARCIAL: {success_count}/3 archivos subidos en {tiempo_total:.2f}s")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Error en sincronizacion con Cloudflare R2: {e}")
            logger.info("La API local sigue funcionando normalmente")
    
    def start(self):
        if self.is_running:
            return
        try:
            # Job 1: Sincronización de caché local cada 30 minutos
            self.scheduler.add_job(
                func=self.sync_cache,
                trigger=IntervalTrigger(minutes=Config.SYNC_INTERVAL_MINUTES),
                id='sync_cache_local',
                name='Sincronización de caché local',
                replace_existing=True
            )
            logger.info(f"Job programado: Caché local cada {Config.SYNC_INTERVAL_MINUTES} minutos")
            
            # Job 2: Sincronización con Cloudflare 3 veces al día
            if Config.CLOUDFLARE_ENABLED:
                # Madrugada: 6:00 AM
                self.scheduler.add_job(
                    func=self.sync_cloudflare,
                    trigger=CronTrigger(hour=6, minute=0),
                    id='sync_cloudflare_morning',
                    name='Cloudflare - Madrugada (6 AM)',
                    replace_existing=True
                )
                
                # Mediodía: 12:00 PM
                self.scheduler.add_job(
                    func=self.sync_cloudflare,
                    trigger=CronTrigger(hour=12, minute=0),
                    id='sync_cloudflare_noon',
                    name='Cloudflare - Mediodía (12 PM)',
                    replace_existing=True
                )
                
                # Tarde: 6:00 PM (18:00)
                self.scheduler.add_job(
                    func=self.sync_cloudflare,
                    trigger=CronTrigger(hour=18, minute=0),
                    id='sync_cloudflare_evening',
                    name='Cloudflare - Tarde (6 PM)',
                    replace_existing=True
                )
                
                logger.info("Jobs programados: Cloudflare R2 a las 6 AM, 12 PM y 6 PM")
                
                # Subida inicial inmediata (solo si no hay datos en R2)
                logger.info("Programando subida inicial a Cloudflare en 2 minutos...")
                self.scheduler.add_job(
                    func=self.sync_cloudflare,
                    trigger='date',
                    run_date=datetime.now().replace(second=0, microsecond=0) + __import__('datetime').timedelta(minutes=2),
                    id='sync_cloudflare_initial',
                    name='Cloudflare - Subida inicial',
                    replace_existing=True
                )
            else:
                logger.info("Cloudflare R2 deshabilitado - No se programaron subidas")
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler iniciado correctamente")
            
        except Exception as e:
            logger.error(f"Error iniciando scheduler: {e}")
            raise

    def stop(self):
        if not self.is_running:
            return
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler detenido")
        except Exception as e:
            logger.error(f"Error deteniendo scheduler: {e}")

    def get_jobs(self):
        return self.scheduler.get_jobs()


task_scheduler = TaskScheduler()
