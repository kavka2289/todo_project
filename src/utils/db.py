from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from src.config import settings
from src.utils.logger import db_logger
import time


# Создаем engine с настройками пула соединений
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db() -> Session:
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация базы данных"""
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        db_logger.info("База данных инициализирована успешно")
    except Exception as e:
        db_logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise


def check_db_connection():
    """Проверка соединения с базой данных"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        db_logger.info("Соединение с базой данных установлено")
        return True
    except Exception as e:
        db_logger.error(f"Ошибка соединения с базой данных: {e}")
        return False


# Логирование SQL запросов в debug режиме
if settings.debug:
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        db_logger.debug(f"SQL: {statement}")

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        if total > 0.1:  # Логируем медленные запросы
            db_logger.warning(f"Slow query ({total:.3f}s): {statement}")
        else:
            db_logger.debug(f"Query executed in {total:.3f}s")
