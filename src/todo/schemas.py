from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.todo.models import TodoStatus


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Название задачи")
    description: Optional[str] = Field(None, max_length=1000, description="Описание задачи")
    status: TodoStatus = Field(default=TodoStatus.PENDING, description="Статус задачи")
    category_id: Optional[int] = Field(None, description="ID категории")
    deadline: Optional[datetime] = Field(None, description="Дедлайн задачи")


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TodoStatus] = None
    category_id: Optional[int] = None
    deadline: Optional[datetime] = None


class TodoStatusUpdate(BaseModel):
    status: TodoStatus


class TodoInDB(TodoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Todo(TodoInDB):
    pass


class TodoWithCategory(Todo):
    category_name: Optional[str] = None
    category_color: Optional[str] = None


class TodoListResponse(BaseModel):
    items: List[TodoWithCategory]
    total: int
    page: int
    size: int
    pages: int


class TodoStats(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    cancelled: int
    overdue: int
