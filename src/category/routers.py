from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.category import crud, schemas
from src.user.schemas import User
from src.utils.db import get_db
from src.utils.permissions import get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: schemas.CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создать новую категорию"""
    try:
        # Проверяем, не существует ли уже категория с таким именем
        existing_category = crud.get_category_by_name(db, category.name, current_user.id)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория с таким именем уже существует"
            )
        
        db_category = crud.create_category(db=db, category=category, user_id=current_user.id)
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании категории"
            )
        
        return db_category
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании категории: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/", response_model=List[schemas.Category])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить список категорий пользователя"""
    try:
        categories = crud.get_categories(db, user_id=current_user.id, skip=skip, limit=limit)
        return categories
    except Exception as e:
        logger.error(f"Ошибка при получении категорий: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/with-counts", response_model=List[schemas.CategoryWithTodoCount])
async def read_categories_with_counts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить категории с количеством задач в каждой"""
    try:
        categories = crud.get_categories_with_todo_count(db, user_id=current_user.id)
        return categories
    except Exception as e:
        logger.error(f"Ошибка при получении категорий с количеством задач: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/{category_id}", response_model=schemas.Category)
async def read_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить категорию по ID"""
    try:
        category = crud.get_category(db, category_id=category_id, user_id=current_user.id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении категории: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put("/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить категорию"""
    try:
        # Проверяем, не существует ли уже категория с таким именем
        if category_update.name:
            existing_category = crud.get_category_by_name(db, category_update.name, current_user.id)
            if existing_category and existing_category.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Категория с таким именем уже существует"
                )
        
        db_category = crud.update_category(
            db=db, 
            category_id=category_id, 
            category_update=category_update, 
            user_id=current_user.id
        )
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        
        return db_category
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении категории: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить категорию"""
    try:
        success = crud.delete_category(db=db, category_id=category_id, user_id=current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        
        return {"message": "Категория успешно удалена"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении категории: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
