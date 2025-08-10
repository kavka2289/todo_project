from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from src.user import crud, schemas
from src.utils.db import get_db
from src.utils.security import create_access_token, create_refresh_token, get_current_user
from src.utils.permissions import get_current_active_user
from src.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/users/login")


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    try:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        user_created = crud.create_user(db=db, user=user)
        if not user_created:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании пользователя"
            )
        
        logger.info(f"Зарегистрирован новый пользователь: {user.email}")
        return user_created
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post("/login", response_model=schemas.Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Авторизация пользователя"""
    try:
        user = crud.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь неактивен"
            )
        
        access_token_expires = settings.access_token_expire_minutes * 60
        refresh_token_expires = settings.refresh_token_expire_days * 24 * 60 * 60
        
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=refresh_token_expires
        )
        
        logger.info(f"Успешная авторизация пользователя: {user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": access_token_expires,
            "refresh_token": refresh_token
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при авторизации пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    refresh_token: str,
    current_user: schemas.User = Depends(get_current_user)
):
    """Обновление токена доступа"""
    try:
        # Здесь должна быть логика проверки refresh token
        # Для простоты просто создаем новый access token
        access_token_expires = settings.access_token_expire_minutes * 60
        
        access_token = create_access_token(
            data={"sub": current_user.email, "user_id": current_user.id},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": access_token_expires,
            "refresh_token": refresh_token
        }
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении токена"
        )


@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_users_me(
    user_update: schemas.UserUpdate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить информацию о текущем пользователе"""
    try:
        updated_user = crud.update_user(db=db, user_id=current_user.id, user_update=user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        return updated_user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post("/change-password")
async def change_password(
    password_change: schemas.PasswordChange,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Изменить пароль текущего пользователя"""
    try:
        success = crud.change_user_password(
            db=db,
            user_id=current_user.id,
            current_password=password_change.current_password,
            new_password=password_change.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный текущий пароль"
            )
        
        return {"message": "Пароль успешно изменен"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при изменении пароля: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить список пользователей (только для администраторов)"""
    # Здесь можно добавить проверку на администратора
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить пользователя по ID (только для администраторов)"""
    # Здесь можно добавить проверку на администратора
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить пользователя (только для администраторов)"""
    # Здесь можно добавить проверку на администратора
    try:
        success = crud.delete_user(db=db, user_id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        return {"message": "Пользователь успешно удален"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
