import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.notifications.models import Notification
from src.user.models import User
from src.todo.models import Todo
from src.utils.security import create_access_token


def test_create_notification(client: TestClient, db_session: Session, test_user_data: dict):
    """Тест создания уведомления"""
    # Создаем пользователя
    user_response = client.post("/api/v1/users/register", json=test_user_data)
    assert user_response.status_code == 201
    user = user_response.json()
    
    # Авторизуемся
    login_response = client.post("/api/v1/users/login", data=test_user_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем уведомление
    notification_data = {
        "type": "test_notification",
        "title": "Test Notification",
        "message": "This is a test notification",
        "priority": "medium"
    }
    
    response = client.post("/api/v1/notifications/", json=notification_data, headers=headers)
    assert response.status_code == 201
    notification = response.json()
    
    assert notification["title"] == "Test Notification"
    assert notification["type"] == "test_notification"
    assert notification["is_read"] == False


def test_get_user_notifications(client: TestClient, db_session: Session, test_user_data: dict):
    """Тест получения уведомлений пользователя"""
    # Создаем пользователя и авторизуемся
    user_response = client.post("/api/v1/users/register", json=test_user_data)
    user = user_response.json()
    
    login_response = client.post("/api/v1/users/login", data=test_user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем несколько уведомлений
    for i in range(3):
        notification_data = {
            "type": f"test_notification_{i}",
            "title": f"Test Notification {i}",
            "message": f"This is test notification {i}",
            "priority": "low"
        }
        client.post("/api/v1/notifications/", json=notification_data, headers=headers)
    
    # Получаем уведомления
    response = client.get("/api/v1/notifications/", headers=headers)
    assert response.status_code == 200
    notifications = response.json()
    
    assert len(notifications) == 3
    assert all(n["user_id"] == user["id"] for n in notifications)


def test_mark_notification_read(client: TestClient, db_session: Session, test_user_data: dict):
    """Тест отметки уведомления как прочитанного"""
    # Создаем пользователя и авторизуемся
    user_response = client.post("/api/v1/users/register", json=test_user_data)
    user = user_response.json()
    
    login_response = client.post("/api/v1/users/login", data=test_user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем уведомление
    notification_data = {
        "type": "test_notification",
        "title": "Test Notification",
        "message": "This is a test notification",
        "priority": "low"
    }
    
    create_response = client.post("/api/v1/notifications/", json=notification_data, headers=headers)
    notification = create_response.json()
    
    # Отмечаем как прочитанное
    response = client.post(f"/api/v1/notifications/{notification['id']}/read", headers=headers)
    assert response.status_code == 200
    
    updated_notification = response.json()
    assert updated_notification["is_read"] == True
    assert updated_notification["read_at"] is not None


def test_get_notification_summary(client: TestClient, db_session: Session, test_user_data: dict):
    """Тест получения сводки уведомлений"""
    # Создаем пользователя и авторизуемся
    user_response = client.post("/api/v1/users/register", json=test_user_data)
    user = user_response.json()
    
    login_response = client.post("/api/v1/users/login", data=test_user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем уведомления с разными приоритетами
    priorities = ["low", "medium", "high"]
    for i, priority in enumerate(priorities):
        notification_data = {
            "type": f"test_notification_{i}",
            "title": f"Test Notification {i}",
            "message": f"This is test notification {i}",
            "priority": priority
        }
        client.post("/api/v1/notifications/", json=notification_data, headers=headers)
    
    # Получаем сводку
    response = client.get("/api/v1/notifications/summary", headers=headers)
    assert response.status_code == 200
    summary = response.json()
    
    assert summary["total"] == 3
    assert summary["unread"] == 3
    assert summary["high_priority"] == 1
    assert summary["medium_priority"] == 1
    assert summary["low_priority"] == 1
    assert len(summary["recent_notifications"]) == 3


def test_clear_all_notifications(client: TestClient, db_session: Session, test_user_data: dict):
    """Тест очистки всех уведомлений"""
    # Создаем пользователя и авторизуемся
    user_response = client.post("/api/v1/users/register", json=test_user_data)
    user = user_response.json()
    
    login_response = client.post("/api/v1/users/login", data=test_user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем несколько уведомлений
    for i in range(3):
        notification_data = {
            "type": f"test_notification_{i}",
            "title": f"Test Notification {i}",
            "message": f"This is test notification {i}",
            "priority": "low"
        }
        client.post("/api/v1/notifications/", json=notification_data, headers=headers)
    
    # Проверяем, что уведомления созданы
    response = client.get("/api/v1/notifications/", headers=headers)
    assert len(response.json()) == 3
    
    # Очищаем все уведомления
    clear_response = client.delete("/api/v1/notifications/", headers=headers)
    assert clear_response.status_code == 204
    
    # Проверяем, что уведомления удалены
    response = client.get("/api/v1/notifications/", headers=headers)
    assert len(response.json()) == 0
