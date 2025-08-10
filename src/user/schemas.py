from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Пароль (минимум 8 символов)")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
