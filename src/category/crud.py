from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from src.category.models import Category
from src.category.schemas import CategoryCreate, CategoryUpdate
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def get_category(db: Session, category_id: int, user_id: int) -> Optional[Category]:
    """Получить категорию по ID для конкретного пользователя"""
    return db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()


def get_categories(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Category]:
    """Получить список категорий пользователя с пагинацией"""
    return db.query(Category).filter(
        Category.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_categories_with_todo_count(db: Session, user_id: int) -> List[dict]:
    """Получить категории с количеством задач в каждой"""
    result = db.query(
        Category,
        func.count(Category.todos).label('todo_count')
    ).outerjoin(Category.todos).filter(
        Category.user_id == user_id
    ).group_by(Category.id).all()
    
    return [
        {
            **category.__dict__,
            'todo_count': todo_count
        }
        for category, todo_count in result
    ]


def create_category(db: Session, category: CategoryCreate, user_id: int) -> Optional[Category]:
    """Создать новую категорию"""
    try:
        db_category = Category(
            **category.dict(),
            user_id=user_id
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        logger.info(f"Создана новая категория: {category.name} для пользователя {user_id}")
        return db_category
    except IntegrityError:
        db.rollback()
        logger.warning(f"Попытка создать категорию с существующим именем: {category.name}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании категории: {e}")
        raise


def update_category(db: Session, category_id: int, category_update: CategoryUpdate, user_id: int) -> Optional[Category]:
    """Обновить категорию"""
    try:
        db_category = get_category(db, category_id, user_id)
        if not db_category:
            return None
        
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        logger.info(f"Обновлена категория: {db_category.name} для пользователя {user_id}")
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении категории {category_id}: {e}")
        raise


def delete_category(db: Session, category_id: int, user_id: int) -> bool:
    """Удалить категорию"""
    try:
        db_category = get_category(db, category_id, user_id)
        if not db_category:
            return False
        
        db.delete(db_category)
        db.commit()
        logger.info(f"Удалена категория: {db_category.name} для пользователя {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при удалении категории {category_id}: {e}")
        raise


def get_category_by_name(db: Session, name: str, user_id: int) -> Optional[Category]:
    """Получить категорию по имени для конкретного пользователя"""
    return db.query(Category).filter(
        Category.name == name,
        Category.user_id == user_id
    ).first()


def get_categories_by_ids(db: Session, category_ids: List[int], user_id: int) -> List[Category]:
    """Получить категории по списку ID для конкретного пользователя"""
    return db.query(Category).filter(
        Category.id.in_(category_ids),
        Category.user_id == user_id
    ).all()
