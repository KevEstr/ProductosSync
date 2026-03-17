"""
Sistema de caché en memoria y disco para optimizar el rendimiento
"""
import json
import time
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps
from src.config import Config
from src.logger import setup_logger

logger = setup_logger(__name__)


class CacheManager:
    """Gestor de caché en memoria y disco"""

    def __init__(self):
        self.memory_cache = {}
        self.cache_dir = Config.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_file(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str, max_age: Optional[int] = None) -> Optional[Any]:
        """
        Obtiene un valor del caché (memoria → disco).
        Retorna None si no existe o expiró.
        """
        max_age = max_age or Config.CACHE_TIMEOUT

        # Memoria primero
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if time.time() - timestamp < max_age:
                return data
            else:
                del self.memory_cache[key]

        # Disco
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                timestamp = cached.get('timestamp', 0)
                if time.time() - timestamp < max_age:
                    data = cached.get('data')
                    self.memory_cache[key] = (data, timestamp)
                    return data
                else:
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"Error leyendo caché {key}: {e}")

        return None

    def set(self, key: str, value: Any) -> None:
        """Guarda un valor en memoria y disco."""
        timestamp = time.time()
        self.memory_cache[key] = (value, timestamp)

        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'data': value
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Error guardando caché {key}: {e}")

    def invalidate(self, key: str) -> None:
        """Invalida una entrada del caché."""
        if key in self.memory_cache:
            del self.memory_cache[key]
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            cache_file.unlink()

    def clear_all(self) -> None:
        """Limpia todo el caché."""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
        logger.info("Caché completamente limpiado")


# Instancia global
cache_manager = CacheManager()


def cached(key_prefix: str, max_age: Optional[int] = None):
    """Decorador para cachear resultados de funciones."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}_{func.__name__}"
            cached_result = cache_manager.get(cache_key, max_age)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            return result
        return wrapper
    return decorator
