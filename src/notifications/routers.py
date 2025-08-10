from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.utils.db import get_db
from src.user.models import User
from src.utils.permissions import get_current_user
from src.notifications import crud, schemas
from src.utils.notifications import check_user_deadlines
from src.utils.logger import app_logger, log_action

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[schemas.Notification])
def get_notifications(
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество уведомлений"),
    unread_only: bool = Query(False, description="Только непрочитанные уведомления"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение уведомлений пользователя"""
    try:
        notifications = crud.get_user_notifications(
            db, current_user.id, skip=skip, limit=limit, unread_only=unread_only
        )
        return notifications
    except Exception as e:
        app_logger.error(f"Ошибка при получении уведомлений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/summary", response_model=schemas.NotificationSummary)
def get_notifications_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение сводки уведомлений"""
    try:
        summary = crud.get_notification_summary(db, current_user.id)
        return schemas.NotificationSummary(**summary)
    except Exception as e:
        app_logger.error(f"Ошибка при получении сводки уведомлений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/deadlines", response_model=List[Dict[str, Any]])
def get_deadline_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение уведомлений о дедлайнах"""
    notifications = check_user_deadlines(db, current_user.id)
    return notifications


@router.post("/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отметить уведомление как прочитанное"""
    try:
        notification = crud.mark_notification_read(db, notification_id, current_user.id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уведомление не найдено"
            )
        
        log_action(app_logger, "notification_marked_read", current_user.id, {"notification_id": notification_id})
        return notification
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Ошибка при отметке уведомления как прочитанного: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_all_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Очистить все уведомления пользователя"""
    try:
        deleted_count = crud.clear_user_notifications(db, current_user.id)
        log_action(app_logger, "notifications_cleared", current_user.id, {"deleted_count": deleted_count})
        return
    except Exception as e:
        app_logger.error(f"Ошибка при очистке уведомлений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
