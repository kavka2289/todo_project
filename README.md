# Todo App - FastAPI Backend

Веб-приложение для управления списком задач, построенное на FastAPI с использованием PostgreSQL и Redis.

## 🚀 Возможности

- **Управление пользователями**: регистрация, авторизация, профиль
- **Управление задачами**: создание, редактирование, удаление, изменение статуса
- **Категории**: организация задач по категориям с цветовой кодировкой
- **Фильтрация**: поиск задач по статусу и категории
- **Статистика**: аналитика по выполненным задачам
- **Безопасность**: JWT токены, хеширование паролей
- **Логирование**: отслеживание всех действий пользователей

## 🏗️ Архитектура

```
src/
├── config.py          # Конфигурация приложения
├── user/             # Модуль пользователей
│   ├── models.py     # Модели данных
│   ├── crud.py       # CRUD операции
│   ├── schemas.py    # Pydantic схемы
│   └── routers.py    # API эндпоинты
├── todo/             # Модуль задач
├── category/         # Модуль категорий
└── utils/            # Утилиты
    ├── db.py         # Настройка базы данных
    ├── security.py   # Безопасность
    ├── permissions.py # Права доступа
    └── logger.py     # Логирование
```

## 🛠️ Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и сессии
- **Alembic** - миграции базы данных
- **Pydantic** - валидация данных
- **JWT** - аутентификация
- **Docker** - контейнеризация

## 📋 Требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL 15+
- Redis 7+

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd todo_project
```

### 2. Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f app
```

### 3. Запуск без Docker

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск приложения
uvicorn main:app --reload
```

## 🔧 Конфигурация

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://todo_user:todo_password@localhost:5432/todo_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
```

## 📚 API Документация

После запуска приложения документация доступна по адресу:

- **Swagger UI**: http://localhost:8000/docs

## 🔐 Аутентификация

API использует JWT токены для аутентификации. Для защищенных эндпоинтов добавьте заголовок:

```
Authorization: Bearer <your-jwt-token>
```

## 📊 Основные эндпоинты

### Пользователи
- `POST /api/v1/users/register` - регистрация
- `POST /api/v1/users/login` - авторизация
- `GET /api/v1/users/me` - профиль пользователя

### Задачи
- `GET /api/v1/todos/` - список задач
- `POST /api/v1/todos/` - создание задачи
- `PUT /api/v1/todos/{id}` - обновление задачи
- `DELETE /api/v1/todos/{id}` - удаление задачи
- `PATCH /api/v1/todos/{id}/status` - изменение статуса

### Категории
- `GET /api/v1/categories/` - список категорий
- `POST /api/v1/categories/` - создание категории
- `PUT /api/v1/categories/{id}` - обновление категории
- `DELETE /api/v1/categories/{id}` - удаление категории

## 🗄️ Миграции базы данных

```bash
# Создание миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С покрытием кода
pytest --cov=src

# Запуск тестов через скрипт
python run_tests.py

# Запуск конкретных тестов
python run_tests.py tests/test_users.py
```

## 📝 Логирование

Приложение ведет логи всех действий пользователей:
- Регистрация и авторизация
- Создание, обновление, удаление задач
- Управление категориями

Логи выводятся в консоль и могут быть перенаправлены в файл.

## 🔒 Безопасность

- Пароли хешируются с использованием bcrypt
- JWT токены с настраиваемым временем жизни
- Проверка прав доступа к ресурсам
- Валидация входных данных через Pydantic

## 🚀 Развертывание

### Production

1. Измените `SECRET_KEY` в `.env`
2. Настройте `DATABASE_URL` для production базы
3. Настройте CORS для вашего домена
4. Используйте reverse proxy (nginx) для SSL

### Docker

```bash
# Сборка образа
docker build -t todo-app .

# Запуск контейнера
docker run -p 8000:8000 todo-app
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для деталей.

## 📞 Поддержка

Если у вас есть вопросы или предложения, создайте issue в репозитории.

## 🔮 Планы развития

- [ ] Экспорт задач в CSV/Excel
- [ ] Повторяющиеся задачи
- [ ] Уведомления о дедлайнах
- [ ] Мобильное приложение
- [ ] Интеграция с календарем
- [ ] Дашборд с графиками
- [ ] API rate limiting
- [ ] WebSocket для real-time уведомлений
- [ ] GraphQL API
- [ ] Микросервисная архитектура

### Проверка качества кода

```bash
# Запуск тестов
python -m pytest

# Тесты с покрытием
python -m pytest --cov=src
```
