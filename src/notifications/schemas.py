from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    type: str = Field(..., description="Тип уведомления")
    title: str = Field(..., description="Заголовок уведомления")
    message: Optional[str] = Field(None, description="Сообщение уведомления")
    priority: str = Field("low", description="Приоритет уведомления")
    todo_id: Optional[int] = Field(None, description="ID связанной задачи")


class NotificationCreate(NotificationBase):
    user_id: int = Field(..., description="ID пользователя")


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None


class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationSummary(BaseModel):
    total: int
    unread: int
    high_priority: int
    medium_priority: int
    low_priority: int
    recent_notifications: list[Notification]
