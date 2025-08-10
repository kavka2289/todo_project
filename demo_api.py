#!/usr/bin/env python3
"""
Демонстрационный скрипт для тестирования API
"""

import requests
import json
from datetime import datetime, timedelta

# Базовый URL API
BASE_URL = "http://localhost:8000/api/v1"

def print_response(response, title):
    """Вывод ответа API"""
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def demo_api():
    """Демонстрация работы API"""
    print("🚀 Демонстрация Todo App API")
    print("="*50)
    
    # 1. Регистрация пользователя
    print("\n1️⃣ Регистрация пользователя")
    user_data = {
        "email": "demo@example.com",
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/register", json=user_data)
        print_response(response, "Регистрация пользователя")
        
        if response.status_code == 201:
            user = response.json()
            user_id = user["id"]
            print(f"✅ Пользователь создан с ID: {user_id}")
        else:
            print("❌ Не удалось создать пользователя")
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к API. Убедитесь, что сервер запущен.")
        return
    
    # 2. Авторизация пользователя
    print("\n2️⃣ Авторизация пользователя")
    login_data = {
        "email": "demo@example.com",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login", data=login_data)
    print_response(response, "Авторизация пользователя")
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print(f"✅ Токен получен: {access_token[:20]}...")
    else:
        print("❌ Не удалось авторизоваться")
        return
    
    # 3. Создание категории
    print("\n3️⃣ Создание категории")
    category_data = {
        "name": "Работа",
        "color": "#FF5733"
    }
    
    response = requests.post(f"{BASE_URL}/categories/", json=category_data, headers=headers)
    print_response(response, "Создание категории")
    
    if response.status_code == 201:
        category = response.json()
        category_id = category["id"]
        print(f"✅ Категория создана с ID: {category_id}")
    else:
        print("❌ Не удалось создать категорию")
        return
    
    # 4. Создание задачи
    print("\n4️⃣ Создание задачи")
    todo_data = {
        "title": "Изучить FastAPI",
        "description": "Изучить документацию и примеры FastAPI",
        "category_id": category_id,
        "deadline": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/todos/", json=todo_data, headers=headers)
    print_response(response, "Создание задачи")
    
    if response.status_code == 201:
        todo = response.json()
        todo_id = todo["id"]
        print(f"✅ Задача создана с ID: {todo_id}")
    else:
        print("❌ Не удалось создать задачу")
        return
    
    # 5. Получение списка задач
    print("\n5️⃣ Получение списка задач")
    response = requests.get(f"{BASE_URL}/todos/", headers=headers)
    print_response(response, "Список задач")
    
    # 6. Обновление статуса задачи
    print("\n6️⃣ Обновление статуса задачи")
    new_status = "in_progress"
    response = requests.patch(f"{BASE_URL}/todos/{todo_id}/status?status={new_status}", headers=headers)
    print_response(response, "Обновление статуса задачи")
    
    # 7. Получение статистики
    print("\n7️⃣ Получение статистики")
    response = requests.get(f"{BASE_URL}/todos/statistics/summary", headers=headers)
    print_response(response, "Статистика задач")
    
    # 8. Получение профиля пользователя
    print("\n8️⃣ Получение профиля пользователя")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print_response(response, "Профиль пользователя")
    
    print("\n🎉 Демонстрация завершена!")
    print("📚 Документация API доступна по адресу: http://localhost:8000/docs")

if __name__ == "__main__":
    demo_api()
