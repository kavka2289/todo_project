#!/usr/bin/env python3
"""
Скрипт для запуска тестов
"""
import subprocess
import sys
import os

def run_tests():
    """Запуск тестов с различными опциями"""
    print("🧪 Запуск тестов Todo App")
    print("="*50)
    
    # Проверяем, что pytest установлен
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Pytest не установлен. Установите его: pip install pytest")
            return False
    except Exception:
        print("❌ Не удалось проверить pytest")
        return False
    
    print("✅ Pytest найден")
    
    # Запускаем тесты
    print("\n🚀 Запуск тестов...")
    
    # Базовые тесты
    print("\n📋 Базовые тесты:")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                          capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ Все тесты прошли успешно!")
        
        # Запускаем тесты с покрытием
        print("\n📊 Тесты с покрытием кода:")
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "--cov=src", "--cov-report=term-missing"])
        
        # Создаем HTML отчет
        print("\n📈 Создание HTML отчета...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "--cov=src", "--cov-report=html"])
        print("📁 HTML отчет создан в папке htmlcov/")
        
        return True
    else:
        print(f"\n❌ Некоторые тесты не прошли")
        return False

def run_specific_tests(test_path=None):
    """Запуск конкретных тестов"""
    if test_path:
        print(f"🎯 Запуск тестов: {test_path}")
        subprocess.run([sys.executable, "-m", "pytest", test_path, "-v"])
    else:
        print("❌ Укажите путь к тестам")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Запуск конкретных тестов
        test_path = sys.argv[1]
        run_specific_tests(test_path)
    else:
        # Запуск всех тестов
        success = run_tests()
        sys.exit(0 if success else 1)
