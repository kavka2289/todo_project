import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.user.crud import create_user, get_user_by_email
from src.user.schemas import UserCreate
from src.utils.security import get_password_hash


class TestUserRegistration:
    """Тесты регистрации пользователей"""
    
    def test_register_user_success(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Тест успешной регистрации пользователя"""
        response = client.post("/api/v1/users/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert data["email"] == test_user_data["email"]
        assert "password" not in data  # Пароль не должен возвращаться
    
    def test_register_user_duplicate_email(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Тест регистрации с существующим email"""
        # Создаем первого пользователя
        response1 = client.post("/api/v1/users/register", json=test_user_data)
        assert response1.status_code == 201
        
        # Пытаемся создать второго с тем же email
        response2 = client.post("/api/v1/users/register", json=test_user_data)
        assert response2.status_code == 400
        assert "уже существует" in response2.json()["detail"]
    
    def test_register_user_invalid_data(self, client: TestClient):
        """Тест регистрации с неверными данными"""
        invalid_data = {"email": "invalid-email", "password": "123"}
        response = client.post("/api/v1/users/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_register_user_missing_fields(self, client: TestClient):
        """Тест регистрации с отсутствующими полями"""
        incomplete_data = {"email": "test@example.com"}
        response = client.post("/api/v1/users/register", json=incomplete_data)
        assert response.status_code == 422


class TestUserLogin:
    """Тесты авторизации пользователей"""
    
    def test_login_user_success(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Тест успешной авторизации"""
        # Сначала регистрируем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        
        # Затем пытаемся войти
        login_data = {
            "username": test_user_data["email"],  # OAuth2PasswordRequestForm использует username
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/users/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_user_invalid_credentials(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Тест авторизации с неверными данными"""
        # Регистрируем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        
        # Пытаемся войти с неверным паролем
        login_data = {
            "username": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/users/login", data=login_data)
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Тест авторизации несуществующего пользователя"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        response = client.post("/api/v1/users/login", data=login_data)
        assert response.status_code == 401


class TestUserProfile:
    """Тесты профиля пользователя"""
    
    def test_get_user_profile_requires_auth(self, client: TestClient):
        """Тест что получение профиля требует аутентификации"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    def test_get_user_profile_with_token(self, client: TestClient, db_session: Session, test_user_data: dict):
        """Тест получения профиля с токеном"""
        # Регистрируем и авторизуем пользователя
        client.post("/api/v1/users/register", json=test_user_data)
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/users/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Получаем профиль
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]


class TestUserCRUD:
    """Тесты CRUD операций с пользователями"""
    
    def test_create_user_in_db(self, db_session: Session, test_user_data: dict):
        """Тест создания пользователя в базе данных"""
        user_create = UserCreate(**test_user_data)
        user = create_user(db_session, user_create)
        assert user is not None
        assert user.email == test_user_data["email"]
        assert user.password_hash != test_user_data["password"]  # Пароль должен быть захеширован
    
    def test_get_user_by_email(self, db_session: Session, test_user_data: dict):
        """Тест получения пользователя по email"""
        user_create = UserCreate(**test_user_data)
        created_user = create_user(db_session, user_create)
        
        found_user = get_user_by_email(db_session, email=test_user_data["email"])
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == created_user.email
