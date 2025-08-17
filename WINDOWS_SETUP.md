# Настройка Todo App в Windows

## �� Быстрый старт

### 1. Активация виртуального окружения
```cmd
# В командной строке:
.venv\Scripts\activate.bat

# Или в PowerShell:
.venv\Scripts\Activate.ps1
```

### 2. Установка зависимостей
```cmd
pip install -r requirements.txt
```

### 3. Запуск приложения
```cmd
python run_app.py
```

## 🔧 Решение проблем

### Проблема: "Выполнение сценариев отключено в этой системе"

**Решение: Изменить политику выполнения PowerShell**
```powershell
# От имени администратора:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Проблема: "Команда не найдена"

**Решение: Использовать полный путь**
```cmd
# Вместо:
python run_app.py

# Использовать:
.venv\Scripts\python.exe run_app.py
```

## 🎯 Основные команды

```cmd
# Проверить версию Python
python --version

# Список установленных пакетов
pip list

# Запуск приложения
python run_app.py

# Запуск тестов
python -m pytest
```
