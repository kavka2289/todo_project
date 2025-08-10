import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Добро пожаловать в Todo App API" in response.json()["message"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_users_endpoint():
    response = client.get("/api/v1/users/")
    # Должен вернуть 404, так как эндпоинт не существует
    assert response.status_code == 404


def test_todos_endpoint():
    response = client.get("/api/v1/todos/")
    # Должен вернуть 401, так как требуется аутентификация
    assert response.status_code == 401


def test_categories_endpoint():
    response = client.get("/api/v1/categories/")
    # Должен вернуть 401, так как требуется аутентификация
    assert response.status_code == 401
