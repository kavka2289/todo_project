from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.config import settings
from src.user.routers import router as user_router
from src.category.routers import router as category_router
from src.todo.routers import router as todo_router
from src.notifications.routers import router as notification_router
from src.utils.logger import app_logger
from src.utils.db import check_db_connection
import time
import traceback

# Создание приложения
app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="API для управления списком задач",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None
)

# Middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для проверки доверенных хостов
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware для измерения времени выполнения запросов"""
    start_time = time.time()
    
    # Логируем начало запроса
    app_logger.info(f"Запрос {request.method} {request.url.path} от {request.client.host}")
    
    response = await call_next(request)
    
    # Вычисляем время выполнения
    process_time = time.time() - start_time
    
    # Добавляем заголовок с временем выполнения
    response.headers["X-Process-Time"] = str(process_time)
    
    # Логируем завершение запроса
    app_logger.info(
        f"Запрос {request.method} {request.url.path} завершен за {process_time:.3f}s "
        f"с кодом {response.status_code}"
    )
    
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Обработчик HTTP исключений"""
    app_logger.warning(
        f"HTTP ошибка {exc.status_code}: {exc.detail} "
        f"для {request.method} {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации"""
    app_logger.warning(
        f"Ошибка валидации для {request.method} {request.url.path}: {exc.errors()}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Ошибка валидации данных",
            "details": exc.errors(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Общий обработчик исключений"""
    app_logger.error(
        f"Неожиданная ошибка для {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Внутренняя ошибка сервера",
            "path": request.url.path
        }
    )


# Подключение роутеров
app.include_router(user_router, prefix=settings.api_v1_prefix)
app.include_router(category_router, prefix=settings.api_v1_prefix)
app.include_router(todo_router, prefix=settings.api_v1_prefix)
app.include_router(notification_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    app_logger.info(f"Запуск приложения {settings.project_name} v{settings.project_version}")
    app_logger.info(f"Окружение: {settings.environment}")
    
    # Проверяем соединение с базой данных
    if check_db_connection():
        app_logger.info("Приложение готово к работе")
    else:
        app_logger.error("Не удалось подключиться к базе данных")


@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    app_logger.info("Остановка приложения")


@app.get("/", tags=["root"])
async def root():
    """Корневой эндпоинт"""
    return {
        "message": f"Добро пожаловать в {settings.project_name} API",
        "version": settings.project_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else None,
        "health": "/health"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Проверка состояния приложения"""
    db_status = check_db_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "timestamp": time.time(),
        "version": settings.project_version,
        "environment": settings.environment,
        "database": "connected" if db_status else "disconnected"
    }


@app.get("/info", tags=["info"])
async def app_info():
    """Информация о приложении"""
    return {
        "name": settings.project_name,
        "version": settings.project_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "cache_enabled": settings.cache_enabled,
        "database_url": settings.database_url.split("@")[-1] if "@" in settings.database_url else "hidden"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
