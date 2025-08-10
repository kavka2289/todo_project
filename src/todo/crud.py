from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
from src.todo.models import Todo, TodoStatus
from src.todo.schemas import TodoCreate, TodoUpdate
from src.category.models import Category
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_todo(db: Session, todo_id: int, user_id: int) -> Optional[Todo]:
    """Получить задачу по ID для конкретного пользователя"""
    return db.query(Todo).filter(
        Todo.id == todo_id,
        Todo.user_id == user_id
    ).first()


def get_todos(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[TodoStatus] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None
) -> List[Todo]:
    """Получить список задач пользователя с фильтрацией"""
    query = db.query(Todo).filter(Todo.user_id == user_id)
    
    if status:
        query = query.filter(Todo.status == status)
    
    if category_id:
        query = query.filter(Todo.category_id == category_id)
    
    if search:
        search_filter = or_(
            Todo.title.ilike(f"%{search}%"),
            Todo.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()


def get_todos_with_category(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[TodoStatus] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None
) -> List[dict]:
    """Получить задачи с информацией о категориях"""
    query = db.query(
        Todo,
        Category.name.label('category_name'),
        Category.color.label('category_color')
    ).outerjoin(Category, Todo.category_id == Category.id).filter(
        Todo.user_id == user_id
    )
    
    if status:
        query = query.filter(Todo.status == status)
    
    if category_id:
        query = query.filter(Todo.category_id == category_id)
    
    if search:
        search_filter = or_(
            Todo.title.ilike(f"%{search}%"),
            Todo.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    result = query.offset(skip).limit(limit).all()
    
    return [
        {
            **todo.__dict__,
            'category_name': category_name,
            'category_color': category_color
        }
        for todo, category_name, category_color in result
    ]


def get_todos_count(
    db: Session, 
    user_id: int,
    status: Optional[TodoStatus] = None,
    category_id: Optional[int] = None
) -> int:
    """Получить общее количество задач пользователя"""
    query = db.query(Todo).filter(Todo.user_id == user_id)
    
    if status:
        query = query.filter(Todo.status == status)
    
    if category_id:
        query = query.filter(Todo.category_id == category_id)
    
    return query.count()


def create_todo(db: Session, todo: TodoCreate, user_id: int) -> Optional[Todo]:
    """Создать новую задачу"""
    try:
        db_todo = Todo(
            **todo.dict(),
            user_id=user_id
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        logger.info(f"Создана новая задача: {todo.title} для пользователя {user_id}")
        return db_todo
    except IntegrityError:
        db.rollback()
        logger.warning(f"Ошибка целостности при создании задачи: {todo.title}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании задачи: {e}")
        raise


def update_todo(db: Session, todo_id: int, todo_update: TodoUpdate, user_id: int) -> Optional[Todo]:
    """Обновить задачу"""
    try:
        db_todo = get_todo(db, todo_id, user_id)
        if not db_todo:
            return None
        
        update_data = todo_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_todo, field, value)
        
        db.commit()
        db.refresh(db_todo)
        logger.info(f"Обновлена задача: {db_todo.title} для пользователя {user_id}")
        return db_todo
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении задачи {todo_id}: {e}")
        raise


def update_todo_status(db: Session, todo_id: int, status: TodoStatus, user_id: int) -> Optional[Todo]:
    """Обновить статус задачи"""
    try:
        db_todo = get_todo(db, todo_id, user_id)
        if not db_todo:
            return None
        
        db_todo.status = status
        db.commit()
        db.refresh(db_todo)
        logger.info(f"Обновлен статус задачи: {db_todo.title} -> {status} для пользователя {user_id}")
        return db_todo
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении статуса задачи {todo_id}: {e}")
        raise


def delete_todo(db: Session, todo_id: int, user_id: int) -> bool:
    """Удалить задачу"""
    try:
        db_todo = get_todo(db, todo_id, user_id)
        if not db_todo:
            return False
        
        db.delete(db_todo)
        db.commit()
        logger.info(f"Удалена задача: {db_todo.title} для пользователя {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при удалении задачи {todo_id}: {e}")
        raise


def get_todo_stats(db: Session, user_id: int) -> dict:
    """Получить статистику по задачам пользователя"""
    try:
        # Общее количество задач
        total = db.query(Todo).filter(Todo.user_id == user_id).count()
        
        # Количество задач по статусам
        pending = db.query(Todo).filter(
            and_(Todo.user_id == user_id, Todo.status == TodoStatus.PENDING)
        ).count()
        
        in_progress = db.query(Todo).filter(
            and_(Todo.user_id == user_id, Todo.status == TodoStatus.IN_PROGRESS)
        ).count()
        
        completed = db.query(Todo).filter(
            and_(Todo.user_id == user_id, Todo.status == TodoStatus.COMPLETED)
        ).count()
        
        cancelled = db.query(Todo).filter(
            and_(Todo.user_id == user_id, Todo.status == TodoStatus.CANCELLED)
        ).count()
        
        # Просроченные задачи
        overdue = db.query(Todo).filter(
            and_(
                Todo.user_id == user_id,
                Todo.deadline < datetime.utcnow(),
                Todo.status.in_([TodoStatus.PENDING, TodoStatus.IN_PROGRESS])
            )
        ).count()
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled,
            "overdue": overdue
        }
    except Exception as e:
        logger.error(f"Ошибка при получении статистики задач: {e}")
        raise


def get_todos_by_deadline(
    db: Session, 
    user_id: int, 
    deadline_from: Optional[datetime] = None,
    deadline_to: Optional[datetime] = None
) -> List[Todo]:
    """Получить задачи по диапазону дедлайнов"""
    query = db.query(Todo).filter(Todo.user_id == user_id)
    
    if deadline_from:
        query = query.filter(Todo.deadline >= deadline_from)
    
    if deadline_to:
        query = query.filter(Todo.deadline <= deadline_to)
    
    return query.all()


def get_todos_by_category(db: Session, user_id: int, category_id: int) -> List[Todo]:
    """Получить все задачи определенной категории"""
    return db.query(Todo).filter(
        Todo.user_id == user_id,
        Todo.category_id == category_id
    ).all()
