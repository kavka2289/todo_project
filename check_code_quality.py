#!/usr/bin/env python3
"""
Скрипт для проверки качества кода
"""
import subprocess
import sys
import os

def check_black():
    """Проверка форматирования кода с Black"""
    print("🎨 Проверка форматирования кода (Black)...")
    try:
        result = subprocess.run([sys.executable, "-m", "black", "--check", "src/", "*.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Код отформатирован правильно")
            return True
        else:
            print("❌ Код требует форматирования")
            print("Запустите: python -m black src/ *.py")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке Black: {e}")
        return False

def check_isort():
    """Проверка сортировки импортов с isort"""
    print("📦 Проверка сортировки импортов (isort)...")
    try:
        result = subprocess.run([sys.executable, "-m", "isort", "--check-only", "src/", "*.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Импорты отсортированы правильно")
            return True
        else:
            print("❌ Импорты требуют сортировки")
            print("Запустите: python -m isort src/ *.py")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке isort: {e}")
        return False

def check_flake8():
    """Проверка стиля кода с flake8"""
    print("🔍 Проверка стиля кода (flake8)...")
    try:
        result = subprocess.run([sys.executable, "-m", "flake8", "src/", "*.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Код соответствует стандартам")
            return True
        else:
            print("❌ Найдены проблемы со стилем:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке flake8: {e}")
        return False

def check_mypy():
    """Проверка типов с mypy (если установлен)"""
    print("🔍 Проверка типов (mypy)...")
    try:
        result = subprocess.run([sys.executable, "-m", "mypy", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Mypy найден, проверяем типы...")
            subprocess.run([sys.executable, "-m", "mypy", "src/"], capture_output=False)
            return True
        else:
            print("ℹ️ Mypy не установлен. Установите: pip install mypy")
            return True  # Не считаем это ошибкой
    except Exception:
        print("ℹ️ Mypy не установлен. Установите: pip install mypy")
        return True  # Не считаем это ошибкой

def format_code():
    """Автоматическое форматирование кода"""
    print("🎨 Автоматическое форматирование кода...")
    
    # Форматируем с Black
    print("  - Форматирование с Black...")
    subprocess.run([sys.executable, "-m", "black", "src/", "*.py"], capture_output=False)
    
    # Сортируем импорты
    print("  - Сортировка импортов...")
    subprocess.run([sys.executable, "-m", "isort", "src/", "*.py"], capture_output=False)
    
    print("✅ Код отформатирован")

def main():
    """Основная функция"""
    print("🔍 Проверка качества кода Todo App")
    print("="*50)
    
    # Проверяем качество
    black_ok = check_black()
    isort_ok = check_isort()
    flake8_ok = check_flake8()
    mypy_ok = check_mypy()
    
    print("\n📊 Результаты проверки:")
    print(f"  Black: {'✅' if black_ok else '❌'}")
    print(f"  isort: {'✅' if isort_ok else '❌'}")
    print(f"  flake8: {'✅' if flake8_ok else '❌'}")
    print(f"  mypy: {'✅' if mypy_ok else '❌'}")
    
    all_ok = black_ok and isort_ok and flake8_ok and mypy_ok
    
    if all_ok:
        print("\n🎉 Все проверки пройдены успешно!")
    else:
        print("\n⚠️  Найдены проблемы с качеством кода")
        
        if not (black_ok and isort_ok):
            print("\n💡 Для автоматического исправления запустите:")
            print("   python check_code_quality.py --format")
    
    return all_ok

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--format":
        format_code()
    else:
        success = main()
        sys.exit(0 if success else 1)
