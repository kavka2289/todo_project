import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.todo.models import Todo, TodoStatus
from src.user.models import User
from src.utils.logger import app_logger
from src.utils.cache import cache_manager, get_cache_key


class NotificationManager:
    """Менеджер уведомлений для приложения"""
    
    def __init__(self):
        self.notification_types = {
            'deadline_approaching': 'Дедлайн приближается',
            'deadline_overdue': 'Дедлайн просрочен',
            'task_completed': 'Задача выполнена',
            'task_created': 'Новая задача создана'
        }
    
    def check_deadlines(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Проверка дедлайнов и создание уведомлений"""
        notifications = []
        now = datetime.utcnow()
        
        # Задачи с приближающимся дедлайном (в течение 24 часов)
        tomorrow = now + timedelta(days=1)
        approaching_deadlines = db.query(Todo).filter(
            Todo.user_id == user_id,
            Todo.deadline <= tomorrow,
            Todo.deadline >= now,
            Todo.status != TodoStatus.COMPLETED
        ).all()
        
        for todo in approaching_deadlines:
            hours_until_deadline = int((todo.deadline - now).total_seconds() / 3600)
            notifications.append({
                'type': 'deadline_approaching',
                'title': f'Дедлайн приближается: {todo.title}',
                'message': f'До дедлайна осталось {hours_until_deadline} часов',
                'todo_id': todo.id,
                'deadline': todo.deadline,
                'priority': 'medium' if hours_until_deadline <= 12 else 'low'
            })
        
        # Просроченные задачи
        overdue_todos = db.query(Todo).filter(
            Todo.user_id == user_id,
            Todo.deadline < now,
            Todo.status != TodoStatus.COMPLETED
        ).all()
        
        for todo in overdue_todos:
            days_overdue = int((now - todo.deadline).total_seconds() / 86400)
            notifications.append({
                'type': 'deadline_overdue',
                'title': f'Дедлайн просрочен: {todo.title}',
                'message': f'Задача просрочена на {days_overdue} дней',
                'todo_id': todo.id,
                'deadline': todo.deadline,
                'priority': 'high'
            })
        
        return notifications
    
    def get_user_notifications(self, db: Session, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение уведомлений пользователя"""
        cache_key = get_cache_key("user", user_id, "notifications")
        
        def fetch_notifications():
            # Получаем уведомления о дедлайнах
            deadline_notifications = self.check_deadlines(db, user_id)
            
            # Получаем последние действия пользователя (из логов)
            # В реальном приложении здесь была бы таблица уведомлений
            
            return deadline_notifications[:limit]
        
        return cache_manager.get_or_set(cache_key, fetch_notifications, ttl=300)
    
    def mark_notification_read(self, user_id: int, notification_id: str):
        """Отметить уведомление как прочитанное"""
        # В реальном приложении здесь была бы таблица уведомлений
        # Пока просто инвалидируем кэш
        cache_key = get_cache_key("user", user_id, "notifications")
        cache_manager.delete(cache_key)
    
    def create_task_notification(self, task_type: str, todo: Todo, user: User) -> Dict[str, Any]:
        """Создание уведомления о задаче"""
        if task_type == 'created':
            return {
                'type': 'task_created',
                'title': f'Новая задача: {todo.title}',
                'message': f'Создана новая задача "{todo.title}"',
                'todo_id': todo.id,
                'priority': 'low'
            }
        elif task_type == 'completed':
            return {
                'type': 'task_completed',
                'title': f'Задача выполнена: {todo.title}',
                'message': f'Задача "{todo.title}" отмечена как выполненная',
                'todo_id': todo.id,
                'priority': 'low'
            }
        
        return None
    
    def get_notification_summary(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Получение сводки уведомлений"""
        notifications = self.get_user_notifications(db, user_id)
        
        summary = {
            'total': len(notifications),
            'high_priority': len([n for n in notifications if n['priority'] == 'high']),
            'medium_priority': len([n for n in notifications if n['priority'] == 'medium']),
            'low_priority': len([n for n in notifications if n['priority'] == 'low']),
            'deadline_approaching': len([n for n in notifications if n['type'] == 'deadline_approaching']),
            'deadline_overdue': len([n for n in notifications if n['type'] == 'deadline_overdue'])
        }
        
        return summary


# Создаем глобальный экземпляр менеджера уведомлений
notification_manager = NotificationManager()


def get_user_notifications(db: Session, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Получение уведомлений пользователя"""
    return notification_manager.get_user_notifications(db, user_id, limit)


def check_user_deadlines(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Проверка дедлайнов пользователя"""
    return notification_manager.check_deadlines(db, user_id)


def create_task_notification(task_type: str, todo: Todo, user: User) -> Dict[str, Any]:
    """Создание уведомления о задаче"""
    return notification_manager.create_task_notification(task_type, todo, user)
