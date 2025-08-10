import pytest
from fastapi.testclient import TestClient


class TestMainApp:
    """Тесты основного приложения"""
    
    def test_read_root(self, client: TestClient):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Todo App" in data["message"]
        assert "version" in data
        assert "environment" in data
    
    def test_health_check(self, client: TestClient):
        """Тест проверки состояния приложения"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
    
    def test_app_info(self, client: TestClient):
        """Тест информации о приложении"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "environment" in data
        assert "debug" in data
    
    def test_docs_available(self, client: TestClient):
        """Тест доступности документации"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema(self, client: TestClient):
        """Тест доступности OpenAPI схемы"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestAPIEndpoints:
    """Тесты API эндпоинтов"""
    
    def test_users_endpoint_requires_auth(self, client: TestClient):
        """Тест что эндпоинт пользователей требует аутентификации"""
        response = client.get("/api/v1/users/")
        assert response.status_code == 401
    
    def test_todos_endpoint_requires_auth(self, client: TestClient):
        """Тест что эндпоинт задач требует аутентификации"""
        response = client.get("/api/v1/todos/")
        assert response.status_code == 401
    
    def test_categories_endpoint_requires_auth(self, client: TestClient):
        """Тест что эндпоинт категорий требует аутентификации"""
        response = client.get("/api/v1/categories/")
        assert response.status_code == 401


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    def test_404_not_found(self, client: TestClient):
        """Тест обработки 404 ошибки"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """Тест обработки метода не разрешен"""
        response = client.post("/")
        assert response.status_code == 405
