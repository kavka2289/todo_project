from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    color: str = Field(default="#000000", description="Цвет категории в hex формате")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, description="Цвет категории в hex формате")


class CategoryInDB(CategoryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Category(CategoryInDB):
    pass


class CategoryWithTodoCount(Category):
    todo_count: int = 0


class CategoryList(BaseModel):
    categories: List[Category]
    total: int
    page: int
    size: int
    pages: int
