"""
Módulo para subir inventario a Cloudflare R2
"""
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__)


class CloudflareUploader:
    """Gestor de subida de archivos a Cloudflare R2"""
    
    def __init__(self):
        self.enabled = Config.CLOUDFLARE_ENABLED
        
        if not self.enabled:
            logger.info("Cloudflare R2 deshabilitado en configuración")
            return
        
        self.account_id = Config.CLOUDFLARE_ACCOUNT_ID
        self.access_key_id = Config.CLOUDFLARE_ACCESS_KEY_ID
        self.secret_access_key = Config.CLOUDFLARE_SECRET_ACCESS_KEY
        self.bucket_name = Config.CLOUDFLARE_BUCKET_NAME
        
        # Validar configuración
        if not all([self.account_id, self.access_key_id, self.secret_access_key, self.bucket_name]):
            logger.warning("Cloudflare R2 habilitado pero faltan credenciales. Deshabilitando...")
            self.enabled = False
            return
        
        # Configurar cliente S3 compatible con R2
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name='auto'
            )
            logger.info("Cliente Cloudflare R2 inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando cliente R2: {e}")
            self.enabled = False
    
    def upload_inventario(self, inventario_data: list) -> bool:
        """
        Sube el inventario a Cloudflare R2 como archivo JSON
        
        Args:
            inventario_data: Lista de productos con inventario
            
        Returns:
            True si se subió correctamente, False en caso contrario
        """
        if not self.enabled:
            logger.debug("Cloudflare R2 deshabilitado, omitiendo subida")
            return False
        
        try:
            # Preparar datos con metadata
            data_to_upload = {
                'success': True,
                'total': len(inventario_data),
                'timestamp': datetime.now().isoformat(),
                'data': inventario_data
            }
            
            # Convertir a JSON
            json_data = json.dumps(data_to_upload, ensure_ascii=False, indent=2)
            
            # Subir a R2
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key='inventario.json',
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                CacheControl='public, max-age=300'  # Cache de 5 minutos
            )
            
            logger.info(f"✓ Inventario subido a Cloudflare R2: {len(inventario_data)} productos")
            return True
            
        except ClientError as e:
            logger.error(f"Error subiendo a Cloudflare R2: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado subiendo a R2: {e}")
            return False
    
    def upload_productos(self, productos_data: list) -> bool:
        """
        Sube la lista de productos a Cloudflare R2
        
        Args:
            productos_data: Lista de productos
            
        Returns:
            True si se subió correctamente, False en caso contrario
        """
        if not self.enabled:
            return False
        
        try:
            data_to_upload = {
                'success': True,
                'total': len(productos_data),
                'timestamp': datetime.now().isoformat(),
                'data': productos_data
            }
            
            json_data = json.dumps(data_to_upload, ensure_ascii=False, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key='productos.json',
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                CacheControl='public, max-age=300'
            )
            
            logger.info(f"✓ Productos subidos a Cloudflare R2: {len(productos_data)} productos")
            return True
            
        except Exception as e:
            logger.error(f"Error subiendo productos a R2: {e}")
            return False
    
    def upload_precios(self, precios_data: list) -> bool:
        """
        Sube los precios a Cloudflare R2
        
        Args:
            precios_data: Lista de precios
            
        Returns:
            True si se subió correctamente, False en caso contrario
        """
        if not self.enabled:
            return False
        
        try:
            data_to_upload = {
                'success': True,
                'total': len(precios_data),
                'timestamp': datetime.now().isoformat(),
                'data': precios_data
            }
            
            json_data = json.dumps(data_to_upload, ensure_ascii=False, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key='precios.json',
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                CacheControl='public, max-age=300'
            )
            
            logger.info(f"✓ Precios subidos a Cloudflare R2: {len(precios_data)} precios")
            return True
            
        except Exception as e:
            logger.error(f"Error subiendo precios a R2: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Cloudflare R2
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        if not self.enabled:
            return False
        
        try:
            # Intentar listar objetos del bucket
            self.s3_client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
            logger.info("✓ Conexión con Cloudflare R2 exitosa")
            return True
        except Exception as e:
            logger.error(f"Error probando conexión con R2: {e}")
            return False


# Instancia global del uploader
cloudflare_uploader = CloudflareUploader()
