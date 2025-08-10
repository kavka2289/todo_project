#!/usr/bin/env python3
"""
Скрипт для запуска миграций базы данных
"""
import subprocess
import sys
import os

def run_migrations():
    """Запуск миграций Alembic"""
    print("Запуск миграций базы данных...")
    
    try:
        # Проверяем, что alembic установлен
        result = subprocess.run([sys.executable, "-m", "alembic", "--version"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Alembic не установлен. Установите его: pip install alembic")
            return False
        
        print("✅ Alembic найден")
        
        # Запускаем миграции
        print("Применение миграций...")
        result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Миграции успешно применены!")
            return True
        else:
            print(f"❌ Ошибка при применении миграций: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при запуске миграций: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
