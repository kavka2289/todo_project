import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.utils.db import Base, get_db
from src.user.models import User
from src.category.models import Category
from src.todo.models import Todo


# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Переопределение зависимости для тестов"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Фикстура для тестовой сессии БД"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента"""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя"""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def test_category_data():
    """Тестовые данные категории"""
    return {
        "name": "Test Category",
        "color": "#FF5733"
    }


@pytest.fixture
def test_todo_data():
    """Тестовые данные задачи"""
    return {
        "title": "Test Todo",
        "description": "Test description",
        "deadline": "2024-12-31T23:59:59"
    }
