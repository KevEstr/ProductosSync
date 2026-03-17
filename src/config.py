import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env SOLO del directorio del proyecto, sin buscar en directorios padres
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / '.env')


class Config:
    """Configuración centralizada del proyecto Product-Sync"""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    API_KEY = os.getenv('API_KEY', '')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')

    # Ruta base donde están las carpetas DbfRed (remoto o local)
    DBF_BASE_PATH = os.getenv('DBF_BASE_PATH', '')
    # Ruta directa a una carpeta DbfRed específica (fallback local para desarrollo)
    DBF_PATH = os.getenv('DBF_PATH', '')
    DBF_ENCODING = os.getenv('DBF_ENCODING', 'latin-1')

    SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', 10))

    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')

    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 10800))  # 3 horas
    CACHE_DIR = Path('data/cache')

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

    @staticmethod
    def get_latest_dbf_path() -> str:
        """
        Busca la carpeta DbfRed más reciente.
        Las carpetas pueden tener formato:
          - DbfRed YYYY-MM-DD HH;MM;SS/DbfRed YYYY-MM-DD HH;MM;SS/  (anidada)
          - DbfRed YYYY-MM-DD HH;MM;SS/  (plana)
          - DbfRed/  (simple)
        """
        def _find_latest_in(base_path: Path) -> str | None:
            if not base_path.exists():
                return None
            dbf_folders = sorted(
                [f for f in base_path.iterdir()
                 if f.is_dir() and f.name.startswith('DbfRed')],
                key=lambda f: f.name,
                reverse=True
            )
            if not dbf_folders:
                return None
            latest = dbf_folders[0]
            # Verificar si hay subcarpeta con el mismo nombre (estructura anidada)
            inner = latest / latest.name
            if inner.exists() and inner.is_dir():
                return str(inner)
            return str(latest)

        # 1. Buscar en DBF_BASE_PATH (ruta remota configurada)
        if Config.DBF_BASE_PATH:
            result = _find_latest_in(Path(Config.DBF_BASE_PATH))
            if result:
                return result

        # 2. Si hay DBF_PATH directo configurado, usarlo
        if Config.DBF_PATH:
            return Config.DBF_PATH

        # 3. Buscar en el directorio actual del proyecto
        result = _find_latest_in(Path('.'))
        if result:
            return result

        return 'DbfRed'

    @staticmethod
    def init_app():
        """Crea directorios necesarios"""
        Config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        Path('logs').mkdir(exist_ok=True)
