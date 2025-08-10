from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.user.models import User
from src.user.schemas import UserCreate, UserUpdate
from src.utils.security import get_password_hash, verify_password
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Получить пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получить пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Получить список пользователей с пагинацией"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> Optional[User]:
    """Создать нового пользователя"""
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            password_hash=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Создан новый пользователь: {user.email}")
        return db_user
    except IntegrityError:
        db.rollback()
        logger.warning(f"Попытка создать пользователя с существующим email: {user.email}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании пользователя: {e}")
        raise


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Обновить пользователя"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        logger.info(f"Обновлен пользователь: {db_user.email}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении пользователя {user_id}: {e}")
        raise


def delete_user(db: Session, user_id: int) -> bool:
    """Удалить пользователя"""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        logger.info(f"Удален пользователь: {db_user.email}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
        raise


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def change_user_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
    """Изменить пароль пользователя"""
    try:
        user = get_user(db, user_id)
        if not user:
            return False
        
        if not verify_password(current_password, user.password_hash):
            return False
        
        user.password_hash = get_password_hash(new_password)
        db.commit()
        logger.info(f"Изменен пароль для пользователя: {user.email}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при изменении пароля пользователя {user_id}: {e}")
        raise
