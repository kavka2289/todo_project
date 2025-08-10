import logging
import sys
import os
from typing import Any, Optional
from src.config import settings


def setup_logger(
    name: str, 
    level: Optional[int] = None, 
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logger with console and file handlers"""
    logger = logging.getLogger(name)
    
    # Устанавливаем уровень логирования
    log_level = level or getattr(logging, settings.log_level.upper())
    logger.setLevel(log_level)
    
    # Очищаем существующие handlers
    logger.handlers.clear()
    
    # Создаем форматтер
    formatter = logging.Formatter(settings.log_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (если указан файл)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Не удалось создать file handler: {e}")
    
    # Отключаем propagation к root logger
    logger.propagate = False
    
    return logger


def log_action(
    logger: logging.Logger, 
    action: str, 
    user_id: int, 
    details: Any = None,
    level: str = "info"
):
    """Log user action with specified level"""
    message = f"User {user_id} performed action: {action}"
    if details:
        message += f" - Details: {details}"
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message)


def log_error(
    logger: logging.Logger, 
    error: Exception, 
    user_id: Optional[int] = None,
    context: str = ""
):
    """Log error with context"""
    message = f"Error occurred: {str(error)}"
    if context:
        message = f"{context} - {message}"
    if user_id:
        message = f"User {user_id} - {message}"
    
    logger.error(message, exc_info=True)


def log_performance(
    logger: logging.Logger, 
    operation: str, 
    duration: float,
    user_id: Optional[int] = None
):
    """Log performance metrics"""
    message = f"Operation '{operation}' took {duration:.3f}s"
    if user_id:
        message = f"User {user_id} - {message}"
    
    if duration > 1.0:  # Логируем медленные операции как warning
        logger.warning(message)
    else:
        logger.info(message)


# Создаем основные логгеры
app_logger = setup_logger("todo_app")
db_logger = setup_logger("todo_db")
security_logger = setup_logger("todo_security")
cache_logger = setup_logger("todo_cache")

# Настройка SQLAlchemy logging
if settings.debug:
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
