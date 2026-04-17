"""
Script de prueba para verificar la conexión con Cloudflare R2
"""
import sys
from src.config import Config
from src.cloudflare_uploader import cloudflare_uploader
from src.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Prueba la conexión con Cloudflare R2"""
    print("=" * 80)
    print("  PRUEBA DE CONEXIÓN CON CLOUDFLARE R2")
    print("=" * 80)
    print()
    
    # Verificar configuración
    print("1. Verificando configuración...")
    print(f"   CLOUDFLARE_ENABLED: {Config.CLOUDFLARE_ENABLED}")
    
    if not Config.CLOUDFLARE_ENABLED:
        print()
        print("❌ Cloudflare R2 está DESHABILITADO en .env")
        print()
        print("Para habilitarlo:")
        print("1. Edita el archivo .env")
        print("2. Cambia CLOUDFLARE_ENABLED=True")
        print("3. Configura las credenciales")
        print()
        return
    
    print(f"   Account ID: {Config.CLOUDFLARE_ACCOUNT_ID[:10]}..." if Config.CLOUDFLARE_ACCOUNT_ID else "   Account ID: NO CONFIGURADO")
    print(f"   Bucket: {Config.CLOUDFLARE_BUCKET_NAME}")
    print()
    
    # Probar conexión
    print("2. Probando conexión con Cloudflare R2...")
    if cloudflare_uploader.test_connection():
        print("   ✅ Conexión exitosa")
    else:
        print("   ❌ Error de conexión")
        print()
        print("Verifica:")
        print("- Que las credenciales en .env sean correctas")
        print("- Que el bucket exista")
        print("- Que el token tenga permisos de lectura/escritura")
        return
    
    print()
    
    # Subir archivo de prueba
    print("3. Subiendo archivo de prueba...")
    test_data = [
        {
            "codigo": "TEST001",
            "descripcion": "Producto de prueba",
            "disponible": 100,
            "precio_venta_1": 10000
        }
    ]
    
    if cloudflare_uploader.upload_inventario(test_data):
        print("   ✅ Archivo de prueba subido correctamente")
    else:
        print("   ❌ Error subiendo archivo de prueba")
        return
    
    print()
    print("=" * 80)
    print("  ✅ TODAS LAS PRUEBAS PASARON")
    print("=" * 80)
    print()
    print("Cloudflare R2 está configurado correctamente.")
    print()
    print("Próximos pasos:")
    print("1. Hacer el bucket público en Cloudflare")
    print("2. Obtener la URL pública del bucket")
    print("3. Acceder a: https://tu-bucket.r2.dev/inventario.json")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrueba cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)
