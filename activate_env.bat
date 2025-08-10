@echo off
echo ========================================
echo    Активация виртуального окружения
echo ========================================
echo.

REM Проверяем существование виртуального окружения
if not exist ".venv\Scripts\activate.bat" (
    echo ОШИБКА: Виртуальное окружение не найдено!
    echo Создайте его командой: python -m venv .venv
    pause
    exit /b 1
)

REM Активируем виртуальное окружение
call .venv\Scripts\activate.bat

REM Проверяем успешность активации
if errorlevel 1 (
    echo ОШИБКА: Не удалось активировать виртуальное окружение!
    pause
    exit /b 1
)

echo.
echo ✓ Виртуальное окружение активировано!
echo ✓ Python: %VIRTUAL_ENV%\Scripts\python.exe
echo.
echo Доступные команды:
echo   python --version     - версия Python
echo   pip list            - список пакетов
echo   python run_app.py   - запуск приложения
echo   python -m pytest    - запуск тестов
echo.

REM Открываем командную строку с активированным окружением
cmd /k
