from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.user.models import User
from src.utils.security import verify_token
from src.utils.logger import security_logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from functools import wraps


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из токена"""
    try:
        token = credentials.credentials
        payload = verify_token(token, "access")
        
        if payload is None:
            security_logger.warning("Попытка доступа с недействительным токеном")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Недействительный токен"
            )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            security_logger.warning("Токен не содержит user_id")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Недействительный токен"
            )
        
        try:
            user_id_int = int(user_id)
        except ValueError:
            security_logger.warning(f"Неверный формат user_id в токене: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Неверный формат токена"
            )
        
        user = db.query(User).filter(User.id == user_id_int).first()
        if user is None:
            security_logger.warning(f"Пользователь с ID {user_id_int} не найден")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Пользователь не найден"
            )
        
        if not user.is_active:
            security_logger.warning(f"Попытка доступа неактивным пользователем: {user_id_int}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Пользователь неактивен"
            )
        
        security_logger.info(f"Пользователь {user_id_int} успешно аутентифицирован")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        security_logger.error(f"Ошибка при аутентификации пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка аутентификации"
        )


def check_todo_permission(todo_user_id: int, current_user: User):
    """Проверка прав доступа к задаче"""
    if todo_user_id != current_user.id:
        security_logger.warning(
            f"Попытка несанкционированного доступа к задаче: "
            f"пользователь {current_user.id} пытается получить доступ к задаче пользователя {todo_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Недостаточно прав для доступа к этой задаче"
        )


def check_category_permission(category_user_id: int, current_user: User):
    """Проверка прав доступа к категории"""
    if category_user_id != current_user.id:
        security_logger.warning(
            f"Попытка несанкционированного доступа к категории: "
            f"пользователь {current_user.id} пытается получить доступ к категории пользователя {category_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Недостаточно прав для доступа к этой категории"
        )


def check_user_permission(target_user_id: int, current_user: User):
    """Проверка прав доступа к пользователю"""
    if target_user_id != current_user.id:
        security_logger.warning(
            f"Попытка несанкционированного доступа к пользователю: "
            f"пользователь {current_user.id} пытается получить доступ к пользователю {target_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Недостаточно прав для доступа к этому пользователю"
        )


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency для проверки активности пользователя"""
    if not current_user.is_active:
        security_logger.warning(f"Попытка доступа неактивным пользователем: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )
    return current_user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Получение текущего активного пользователя (алиас для require_active_user)"""
    return require_active_user(current_user)


def admin_required(current_user: User = Depends(get_current_user)) -> User:
    """Dependency для проверки прав администратора"""
    # Здесь можно добавить проверку роли администратора
    # Пока просто проверяем, что пользователь активен
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )
    return current_user


def rate_limit_check(user_id: int, action: str, limit: int = 100, window: int = 3600):
    """Простая проверка ограничения скорости (rate limiting)"""
    # Здесь можно реализовать проверку через Redis
    # Пока просто логируем действие
    security_logger.info(f"Rate limit check для пользователя {user_id}, действие: {action}")


def audit_log(action: str, user_id: int, resource_type: str = None, resource_id: int = None):
    """Логирование действий для аудита"""
    log_message = f"AUDIT: Пользователь {user_id} выполнил действие '{action}'"
    if resource_type and resource_id:
        log_message += f" с ресурсом {resource_type}:{resource_id}"
    
    security_logger.info(log_message)
