from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from src.notifications.models import Notification
from src.notifications.schemas import NotificationCreate, NotificationUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    """Создать новое уведомление"""
    try:
        db_notification = Notification(**notification.dict())
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        logger.info(f"Создано уведомление для пользователя {notification.user_id}")
        return db_notification
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании уведомления: {e}")
        raise


def get_user_notifications(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 50,
    unread_only: bool = False
) -> List[Notification]:
    """Получить уведомления пользователя"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_notification(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Получить уведомление по ID"""
    return db.query(Notification).filter(
        and_(Notification.id == notification_id, Notification.user_id == user_id)
    ).first()


def mark_notification_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Отметить уведомление как прочитанное"""
    try:
        notification = get_notification(db, notification_id, user_id)
        if not notification:
            return None
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        db.commit()
        db.refresh(notification)
        logger.info(f"Уведомление {notification_id} отмечено как прочитанное")
        return notification
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при отметке уведомления как прочитанного: {e}")
        raise


def mark_all_notifications_read(db: Session, user_id: int) -> int:
    """Отметить все уведомления пользователя как прочитанные"""
    try:
        result = db.query(Notification).filter(
            and_(Notification.user_id == user_id, Notification.is_read == False)
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        logger.info(f"Отмечено {result} уведомлений как прочитанные для пользователя {user_id}")
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при отметке всех уведомлений как прочитанных: {e}")
        raise


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    """Удалить уведомление"""
    try:
        notification = get_notification(db, notification_id, user_id)
        if not notification:
            return False
        
        db.delete(notification)
        db.commit()
        logger.info(f"Удалено уведомление {notification_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при удалении уведомления: {e}")
        raise


def clear_user_notifications(db: Session, user_id: int) -> int:
    """Очистить все уведомления пользователя"""
    try:
        result = db.query(Notification).filter(Notification.user_id == user_id).delete()
        db.commit()
        logger.info(f"Очищено {result} уведомлений для пользователя {user_id}")
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при очистке уведомлений: {e}")
        raise


def get_notification_summary(db: Session, user_id: int) -> dict:
    """Получить сводку уведомлений пользователя"""
    try:
        total = db.query(Notification).filter(Notification.user_id == user_id).count()
        unread = db.query(Notification).filter(
            and_(Notification.user_id == user_id, Notification.is_read == False)
        ).count()
        
        high_priority = db.query(Notification).filter(
            and_(Notification.user_id == user_id, Notification.priority == "high")
        ).count()
        
        medium_priority = db.query(Notification).filter(
            and_(Notification.user_id == user_id, Notification.priority == "medium")
        ).count()
        
        low_priority = db.query(Notification).filter(
            and_(Notification.user_id == user_id, Notification.priority == "low")
        ).count()
        
        recent = get_user_notifications(db, user_id, limit=5)
        
        return {
            "total": total,
            "unread": unread,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "recent_notifications": recent
        }
    except Exception as e:
        logger.error(f"Ошибка при получении сводки уведомлений: {e}")
        raise
