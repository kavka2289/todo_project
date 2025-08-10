# Настройка Todo App в Windows

## 🚀 Быстрый старт

### Вариант 1: Через batch файл (рекомендуется)
```cmd
# Двойной клик на файл или в командной строке:
activate_env.bat
```

### Вариант 2: Через PowerShell
```powershell
# Если политика выполнения разрешена:
.\activate_env.ps1

# Или вручную:
.venv\Scripts\activate.ps1
```

### Вариант 3: Через Makefile
```cmd
# Создать и настроить окружение:
make windows-setup

# Активировать существующее:
make venv-activate
```

## 🔧 Решение проблем

### Проблема: "Выполнение сценариев отключено в этой системе"

**Решение 1: Изменить политику выполнения PowerShell**
```powershell
# От имени администратора:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Или для текущего пользователя:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

**Решение 2: Использовать batch файл**
```cmd
activate_env.bat
```

**Решение 3: Прямой вызов Python**
```cmd
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe run_app.py
```

### Проблема: "Команда не найдена"

**Решение: Использовать полный путь**
```cmd
# Вместо:
python run_app.py

# Использовать:
.venv\Scripts\python.exe run_app.py
```

## 📁 Структура файлов активации

- `activate_env.bat` - Batch файл для cmd
- `activate_env.ps1` - PowerShell скрипт
- `Makefile` - Команды make для Windows

## 🎯 Полезные команды

После активации виртуального окружения:

```cmd
# Проверить версию Python
python --version

# Список установленных пакетов
pip list

# Запуск приложения
python run_app.py

# Запуск тестов
python -m pytest

# Проверка качества кода
python check_code_quality.py
```

## 🔄 Переключение между окружениями

Если у вас несколько проектов:

```cmd
# Деактивация текущего окружения
deactivate

# Активация другого проекта
cd C:\path\to\other\project
activate_env.bat
```

## 💡 Советы

1. **Используйте Windows Terminal** - лучший терминал для Windows
2. **Создайте ярлыки** на рабочий стол для часто используемых команд
3. **Используйте VS Code** с интегрированным терминалом
4. **Настройте PowerShell профиль** для автоматической активации

## 🆘 Если ничего не помогает

1. Удалите папку `.venv`
2. Создайте заново: `python -m venv .venv`
3. Активируйте: `activate_env.bat`
4. Установите зависимости: `pip install -r requirements.txt`

## 📞 Поддержка

Если у вас возникли проблемы:
1. Проверьте версию Python (должна быть 3.8+)
2. Убедитесь, что pip обновлен: `python -m pip install --upgrade pip`
3. Проверьте права доступа к папке проекта
