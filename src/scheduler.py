"""
Programador de tareas para sincronización automática
"""
import os
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
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

            logger.info(f"Cache actualizado: {len(inventario)} productos en {(datetime.now() - inicio).total_seconds():.2f}s")
            
            # Subir a Cloudflare R2 si está habilitado
            if Config.CLOUDFLARE_ENABLED:
                try:
                    cloudflare_uploader.upload_inventario(inventario)
                    
                    # También subir productos y precios
                    productos = self.dbf_reader.get_productos(activos_solo=True)
                    cloudflare_uploader.upload_productos(productos)
                    
                    precios = self.dbf_reader.get_precios()
                    cloudflare_uploader.upload_precios(precios)
                    
                except Exception as cf_error:
                    logger.error(f"Error subiendo a Cloudflare R2: {cf_error}")
                    # No fallar la sincronización si falla Cloudflare

        except Exception as e:
            logger.error(f"Error en sincronizacion: {e}")
            # NO borrar el caché cuando falla - mantener datos anteriores
            logger.info("Manteniendo caché anterior debido al error")
    
    def start(self):
        if self.is_running:
            return
        try:
            self.scheduler.add_job(
                func=self.sync_cache,
                trigger=IntervalTrigger(minutes=Config.SYNC_INTERVAL_MINUTES),
                id='sync_cache',
                replace_existing=True
            )
            self.scheduler.start()
            self.is_running = True
            logger.info(f"Scheduler iniciado. Intervalo: {Config.SYNC_INTERVAL_MINUTES} minutos")
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
