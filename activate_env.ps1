# PowerShell скрипт для активации виртуального окружения
param(
    [string]$Path = ".venv"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Активация виртуального окружения" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверяем существование виртуального окружения
if (-not (Test-Path "$Path\Scripts\activate.ps1")) {
    Write-Host "ОШИБКА: Виртуальное окружение не найдено!" -ForegroundColor Red
    Write-Host "Создайте его командой: python -m venv $Path" -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

try {
    # Активируем виртуальное окружение
    & "$Path\Scripts\activate.ps1"
    
    Write-Host ""
    Write-Host "✓ Виртуальное окружение активировано!" -ForegroundColor Green
    Write-Host "✓ Python: $Path\Scripts\python.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "Доступные команды:" -ForegroundColor Yellow
    Write-Host "  python --version     - версия Python" -ForegroundColor White
    Write-Host "  pip list            - список пакетов" -ForegroundColor White
    Write-Host "  python run_app.py   - запуск приложения" -ForegroundColor White
    Write-Host "  python -m pytest    - запуск тестов" -ForegroundColor White
    Write-Host ""
    
    # Показываем текущую директорию и Python
    Write-Host "Текущая директория: $(Get-Location)" -ForegroundColor Gray
    Write-Host "Python: $(Get-Command python | Select-Object -ExpandProperty Source)" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "ОШИБКА: Не удалось активировать виртуальное окружение!" -ForegroundColor Red
    Write-Host "Детали: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
