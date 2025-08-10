#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""
import asyncio
from src.utils.db import engine
from src.user.models import User
from src.category.models import Category
from src.todo.models import Todo
from src.notifications.models import Notification
from src.config import settings

def init_db():
    """Создание всех таблиц в базе данных"""
    print("Создание таблиц в базе данных...")
    
    # Создание таблиц
    User.metadata.create_all(bind=engine)
    Category.metadata.create_all(bind=engine)
    Todo.metadata.create_all(bind=engine)
    Notification.metadata.create_all(bind=engine)
    
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()
