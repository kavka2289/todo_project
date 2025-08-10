# 🚀 Быстрый старт Todo App

## 📋 Предварительные требования

- Python 3.11+
- Docker и Docker Compose (для запуска с контейнерами)
- Git

## 🎯 Вариант 1: Запуск с Docker (Рекомендуется)

### 1. Клонирование и запуск

```bash
# Клонирование репозитория
git clone <repository-url>
cd todo_project

# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f app
```

### 2. Проверка работы

- **API**: http://localhost:8000
- **Документация**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 3. Остановка

```bash
docker-compose down
```

## 🐍 Вариант 2: Запуск без Docker

### 1. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Запуск PostgreSQL и Redis (если установлены локально)
# Или используйте Docker только для БД:
docker-compose up -d postgres redis

# Создание файла .env
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Инициализация базы данных

```bash
# Создание таблиц
python init_db.py

# Или использование Alembic
python run_migrations.py
```

### 4. Запуск приложения

```bash
# Простой запуск
python run_app.py

# Или напрямую
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Тестирование API

### Автоматическое тестирование

```bash
# Запуск тестов
pytest

# С покрытием кода
pytest --cov=src
```

### Ручное тестирование

```bash
# Демонстрация API
python demo_api.py
```

## 📱 Примеры использования API

### 1. Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
```

### 2. Авторизация

```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
```

### 3. Создание задачи (с токеном)

```bash
curl -X POST "http://localhost:8000/api/v1/todos/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"title": "Моя первая задача", "description": "Описание задачи"}'
```

## 🔧 Устранение неполадок

### Проблема: Не удается подключиться к базе данных

**Решение:**
1. Проверьте, что PostgreSQL запущен
2. Проверьте настройки в `.env` файле
3. Убедитесь, что база данных `todo_db` существует

### Проблема: Ошибка импорта модулей

**Решение:**
1. Убедитесь, что вы находитесь в корневой папке проекта
2. Проверьте, что виртуальное окружение активировано
3. Переустановите зависимости: `pip install -r requirements.txt`

### Проблема: Порт 8000 занят

**Решение:**
1. Измените порт в `main.py` или `run_app.py`
2. Или остановите процесс, использующий порт 8000

## 📚 Дополнительные ресурсы

- **FastAPI документация**: https://fastapi.tiangolo.com/
- **SQLAlchemy документация**: https://docs.sqlalchemy.org/
- **Alembic документация**: https://alembic.sqlalchemy.org/

## 🆘 Получение помощи

Если у вас возникли проблемы:

1. Проверьте логи приложения
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки базы данных
4. Создайте issue в репозитории проекта

---

**🎉 Готово! Ваше Todo App запущено и готово к использованию!**