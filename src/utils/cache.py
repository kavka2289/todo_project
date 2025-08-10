import redis
import json
import pickle
from typing import Any, Optional, Union, Callable
from src.config import settings
from src.utils.logger import cache_logger
import time


class CacheManager:
    """Менеджер кэширования для приложения"""
    
    def __init__(self, default_ttl: int = None):
        self.default_ttl = default_ttl or settings.cache_default_ttl
        self.enabled = settings.cache_enabled
        
        if self.enabled:
            try:
                self.client = redis.from_url(settings.redis_url, decode_responses=False)
                # Проверяем соединение
                self.client.ping()
                cache_logger.info("Redis соединение установлено успешно")
            except Exception as e:
                cache_logger.error(f"Ошибка подключения к Redis: {e}")
                self.enabled = False
                self.client = None
        else:
            self.client = None
            cache_logger.info("Кэширование отключено")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Установка значения в кэш"""
        if not self.enabled or not self.client:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                serialized_value = pickle.dumps(value)
            else:
                serialized_value = str(value).encode('utf-8')
            
            ttl = ttl or self.default_ttl
            result = self.client.setex(key, ttl, serialized_value)
            
            if result:
                cache_logger.debug(f"Значение установлено в кэш: {key}, TTL: {ttl}s")
            return bool(result)
        except Exception as e:
            cache_logger.error(f"Ошибка при установке кэша {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        if not self.enabled or not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value is None:
                cache_logger.debug(f"Кэш-промах для ключа: {key}")
                return None
            
            # Пытаемся десериализовать как pickle, если не получилось - как строку
            try:
                result = pickle.loads(value)
                cache_logger.debug(f"Значение получено из кэша: {key}")
                return result
            except:
                result = value.decode('utf-8')
                cache_logger.debug(f"Строковое значение получено из кэша: {key}")
                return result
        except Exception as e:
            cache_logger.error(f"Ошибка при получении кэша {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Удаление значения из кэша"""
        if not self.enabled or not self.client:
            return False
        
        try:
            result = bool(self.client.delete(key))
            if result:
                cache_logger.debug(f"Ключ удален из кэша: {key}")
            return result
        except Exception as e:
            cache_logger.error(f"Ошибка при удалении кэша {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        if not self.enabled or not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            cache_logger.error(f"Ошибка при проверке кэша {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Очистка кэша по паттерну"""
        if not self.enabled or not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted_count = self.client.delete(*keys)
                cache_logger.info(f"Удалено {deleted_count} ключей по паттерну: {pattern}")
                return deleted_count
            return 0
        except Exception as e:
            cache_logger.error(f"Ошибка при очистке кэша по паттерну {pattern}: {e}")
            return 0
    
    def get_or_set(self, key: str, callback: Callable, ttl: Optional[int] = None) -> Any:
        """Получение из кэша или установка через callback"""
        if not self.enabled:
            return callback()
        
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Выполняем callback и кэшируем результат
        value = callback()
        if value is not None:
            self.set(key, value, ttl)
        
        return value
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Увеличение числового значения"""
        if not self.enabled or not self.client:
            return None
        
        try:
            result = self.client.incr(key, amount)
            cache_logger.debug(f"Значение увеличено для ключа {key}: {result}")
            return result
        except Exception as e:
            cache_logger.error(f"Ошибка при увеличении значения для ключа {key}: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """Установка TTL для существующего ключа"""
        if not self.enabled or not self.client:
            return False
        
        try:
            result = bool(self.client.expire(key, ttl))
            if result:
                cache_logger.debug(f"TTL установлен для ключа {key}: {ttl}s")
            return result
        except Exception as e:
            cache_logger.error(f"Ошибка при установке TTL для ключа {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """Получение оставшегося TTL для ключа"""
        if not self.enabled or not self.client:
            return None
        
        try:
            ttl = self.client.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            cache_logger.error(f"Ошибка при получении TTL для ключа {key}: {e}")
            return None
    
    def flush_all(self) -> bool:
        """Очистка всего кэша"""
        if not self.enabled or not self.client:
            return False
        
        try:
            result = self.client.flushdb()
            cache_logger.info("Весь кэш очищен")
            return bool(result)
        except Exception as e:
            cache_logger.error(f"Ошибка при очистке всего кэша: {e}")
            return False


# Создаем глобальный экземпляр менеджера кэша
cache_manager = CacheManager()


def get_cache_key(prefix: str, **kwargs) -> str:
    """Генерация ключа кэша"""
    key_parts = [prefix]
    for k, v in sorted(kwargs.items()):
        if v is not None:
            key_parts.append(f"{k}:{v}")
    return ":".join(key_parts)


def invalidate_user_cache(user_id: int):
    """Инвалидация кэша пользователя"""
    if not cache_manager.enabled:
        return
    
    patterns = [
        f"user:{user_id}:todos:*",
        f"user:{user_id}:categories:*",
        f"user:{user_id}:statistics:*",
        f"user:{user_id}:timeline:*"
    ]
    
    total_deleted = 0
    for pattern in patterns:
        deleted = cache_manager.clear_pattern(pattern)
        total_deleted += deleted
    
    if total_deleted > 0:
        cache_logger.info(f"Инвалидирован кэш пользователя {user_id}: удалено {total_deleted} ключей")


def cache_with_ttl(ttl: int = None):
    """Декоратор для кэширования функций"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            if not cache_manager.enabled:
                return func(*args, **kwargs)
            
            # Создаем ключ кэша на основе имени функции и аргументов
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            return cache_manager.get_or_set(cache_key, lambda: func(*args, **kwargs), ttl)
        return wrapper
    return decorator
