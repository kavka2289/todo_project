# Настройка PyCharm для Todo App

## 1. Интерпретатор Python

1. Откройте `File` → `Settings` → `Project: todo_project` → `Python Interpreter`
2. Создайте новый виртуальный интерпретатор:
   - Нажмите шестеренку → `Add`
   - Выберите `Virtualenv Environment` → `New environment`
   - Base interpreter: выберите Python 3.9+
   - Location: `./venv`

## 2. Установка зависимостей

```bash
# В терминале PyCharm
pip install -r requirements.txt
```

## 3. Настройка инструментов

### Black (форматирование)
1. `File` → `Settings` → `Tools` → `External Tools`
2. Добавьте новый инструмент:
   - Name: `Black`
   - Program: `$ProjectFileDir$/venv/Scripts/black.exe`
   - Arguments: `$FilePath$`
   - Working directory: `$ProjectFileDir$`

### isort (сортировка импортов)
1. Добавьте еще один инструмент:
   - Name: `isort`
   - Program: `$ProjectFileDir$/venv/Scripts/isort.exe`
   - Arguments: `$FilePath$`
   - Working directory: `$ProjectFileDir$`

### flake8 (линтер)
1. `File` → `Settings` → `Project: todo_project` → `Python Integrated Tools`
2. Включите `flake8` в `Code Quality Tools`

## 4. Настройка тестирования

1. `File` → `Settings` → `Project: todo_project` → `Python Integrated Tools`
2. В `Testing` выберите `pytest` как default test runner
3. В `Test Runner` укажите путь к pytest: `./venv/Scripts/pytest.exe`

## 5. Горячие клавиши

Настройте горячие клавиши для инструментов:
- `Ctrl+Shift+B` - Black форматирование
- `Ctrl+Shift+I` - isort сортировка
- `Ctrl+Shift+T` - Запуск тестов

## 6. Автоматизация

Включите автоматическое форматирование при сохранении:
1. `File` → `Settings` → `Tools` → `Actions on Save`
2. Отметьте `Reformat code` и `Optimize imports`

## 7. Запуск конфигураций

Создайте конфигурации запуска:
1. `Run` → `Edit Configurations`
2. Добавьте Python конфигурации:
   - `Run App`: `run_app.py`
   - `Run Tests`: `run_tests.py`
   - `Demo API`: `demo_api.py`
   - `Performance Monitor`: `performance_monitor.py`
