import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    API_KEY = os.getenv('API_KEY', '')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    PORT = int(os.getenv('PORT', 8090))
    HOST = os.getenv('HOST', '0.0.0.0')

    DBF_PATH = os.getenv('DBF_PATH', '../DbfRed')
    DBF_ENCODING = os.getenv('DBF_ENCODING', 'latin-1')

    SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', 30))

    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')

    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 10800))
    CACHE_DIR = Path('data/cache')

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

    # Cloudflare R2 Configuration
    CLOUDFLARE_ENABLED = os.getenv('CLOUDFLARE_ENABLED', 'False').lower() == 'true'
    CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID', '')
    CLOUDFLARE_ACCESS_KEY_ID = os.getenv('CLOUDFLARE_ACCESS_KEY_ID', '')
    CLOUDFLARE_SECRET_ACCESS_KEY = os.getenv('CLOUDFLARE_SECRET_ACCESS_KEY', '')
    CLOUDFLARE_BUCKET_NAME = os.getenv('CLOUDFLARE_BUCKET_NAME', '')

    @staticmethod
    def init_app():
        Config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        Path('logs').mkdir(exist_ok=True)
