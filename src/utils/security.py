from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import settings
from src.utils.logger import security_logger
# from src.user.crud import get_user_by_id  # Убираем для избежания циклического импорта

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема аутентификации
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        security_logger.error(f"Ошибка при проверке пароля: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Получение хеша пароля"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        security_logger.error(f"Ошибка при хешировании пароля: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке пароля"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание access токена"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        security_logger.info(f"Access токен создан для пользователя: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        security_logger.error(f"Ошибка при создании access токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании токена"
        )


def create_refresh_token(data: dict) -> str:
    """Создание refresh токена"""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        security_logger.info(f"Refresh токен создан для пользователя: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        security_logger.error(f"Ошибка при создании refresh токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании refresh токена"
        )


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Проверка токена"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Проверяем тип токена
        if payload.get("type") != token_type:
            security_logger.warning(f"Неверный тип токена: ожидался {token_type}, получен {payload.get('type')}")
            return None
        
        # Проверяем срок действия
        if datetime.fromtimestamp(payload.get("exp", 0)) < datetime.utcnow():
            security_logger.warning("Токен истек")
            return None
        
        return payload
    except JWTError as e:
        security_logger.warning(f"JWT ошибка: {e}")
        return None
    except Exception as e:
        security_logger.error(f"Ошибка при проверке токена: {e}")
        return None


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Обновление access токена"""
    try:
        payload = verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        # Создаем новый access токен
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return create_access_token(data={"sub": user_id})
    except Exception as e:
        security_logger.error(f"Ошибка при обновлении access токена: {e}")
        return None


def validate_password_strength(password: str) -> bool:
    """Валидация сложности пароля"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special


def generate_password_reset_token(email: str) -> str:
    """Генерация токена для сброса пароля"""
    try:
        data = {
            "sub": email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    except Exception as e:
        security_logger.error(f"Ошибка при создании токена сброса пароля: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании токена сброса пароля"
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получение текущего пользователя из токена"""
    try:
        token = credentials.credentials
        payload = verify_token(token, "access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный или истекший токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Здесь можно добавить получение пользователя из базы данных
        # user = get_user_by_id(user_id)
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Пользователь не найден",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )
        
        return {"id": user_id, "token_data": payload}
    except Exception as e:
        security_logger.error(f"Ошибка при получении текущего пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка аутентификации",
            headers={"WWW-Authenticate": "Bearer"},
        )
