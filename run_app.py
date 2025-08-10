#!/usr/bin/env python3
"""
Скрипт для запуска приложения
"""
import uvicorn
from src.config import settings

def main():
    """Запуск приложения"""
    print(f"🚀 Запуск {settings.project_name} v{settings.project_version}")
    print(f"📖 Документация: http://localhost:8000/docs")
    print(f"🔍 ReDoc: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
