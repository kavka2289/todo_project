from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.todo import crud, schemas
from src.todo.models import TodoStatus
from src.user.schemas import User
from src.utils.db import get_db
from src.utils.permissions import get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=schemas.Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: schemas.TodoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создать новую задачу"""
    try:
        # Проверяем существование категории, если указана
        if todo.category_id:
            from src.category.crud import get_category
            category = get_category(db, todo.category_id, current_user.id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Указанная категория не существует"
                )
        
        db_todo = crud.create_todo(db=db, todo=todo, user_id=current_user.id)
        if not db_todo:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании задачи"
            )
        
        return db_todo
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/", response_model=schemas.TodoListResponse)
async def read_todos(
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей"),
    status: Optional[TodoStatus] = Query(None, description="Фильтр по статусу"),
    category_id: Optional[int] = Query(None, description="Фильтр по категории"),
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить список задач пользователя с фильтрацией и пагинацией"""
    try:
        # Получаем задачи с информацией о категориях
        todos = crud.get_todos_with_category(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=status,
            category_id=category_id,
            search=search
        )
        
        # Получаем общее количество для пагинации
        total = crud.get_todos_count(
            db=db,
            user_id=current_user.id,
            status=status,
            category_id=category_id
        )
        
        # Вычисляем параметры пагинации
        page = (skip // limit) + 1
        pages = (total + limit - 1) // limit
        
        return schemas.TodoListResponse(
            items=todos,
            total=total,
            page=page,
            size=limit,
            pages=pages
        )
    
    except Exception as e:
        logger.error(f"Ошибка при получении задач: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/stats", response_model=schemas.TodoStats)
async def get_todo_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить статистику по задачам пользователя"""
    try:
        stats = crud.get_todo_stats(db=db, user_id=current_user.id)
        return schemas.TodoStats(**stats)
    except Exception as e:
        logger.error(f"Ошибка при получении статистики задач: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/{todo_id}", response_model=schemas.Todo)
async def read_todo(
    todo_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить задачу по ID"""
    try:
        todo = crud.get_todo(db, todo_id=todo_id, user_id=current_user.id)
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        return todo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении задачи: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put("/{todo_id}", response_model=schemas.Todo)
async def update_todo(
    todo_id: int,
    todo_update: schemas.TodoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить задачу"""
    try:
        # Проверяем существование категории, если изменяется
        if todo_update.category_id:
            from src.category.crud import get_category
            category = get_category(db, todo_update.category_id, current_user.id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Указанная категория не существует"
                )
        
        db_todo = crud.update_todo(
            db=db, 
            todo_id=todo_id, 
            todo_update=todo_update, 
            user_id=current_user.id
        )
        if not db_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        
        return db_todo
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении задачи: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.patch("/{todo_id}/status", response_model=schemas.Todo)
async def update_todo_status(
    todo_id: int,
    status_update: schemas.TodoStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить статус задачи"""
    try:
        db_todo = crud.update_todo_status(
            db=db, 
            todo_id=todo_id, 
            status=status_update.status, 
            user_id=current_user.id
        )
        if not db_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        
        return db_todo
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса задачи: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить задачу"""
    try:
        success = crud.delete_todo(db=db, todo_id=todo_id, user_id=current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )
        
        return {"message": "Задача успешно удалена"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении задачи: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/category/{category_id}", response_model=List[schemas.Todo])
async def read_todos_by_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить все задачи определенной категории"""
    try:
        # Проверяем существование категории
        from src.category.crud import get_category
        category = get_category(db, category_id, current_user.id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        
        todos = crud.get_todos_by_category(db=db, user_id=current_user.id, category_id=category_id)
        return todos
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении задач по категории: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
