import jwt
from fastapi import Depends, HTTPException, status

from src.config import settings
from src.dao import UserDAO
from src.models import User
from src.service.auth import oauth2_scheme


async def get_current_user(
        access_token: str = Depends(oauth2_scheme),
        db_user: UserDAO = Depends()
) -> User:
    """Получение текущего пользователя из access токена.

    Args:
        access_token (str): Access токен из заголовка Authorization
        db_user (UserDAO): DAO для работы с пользователями

    Returns:
        User: Модель пользователя

    Raises:
        HTTPException: 401 если токен невалидный, истек или пользователь не найден
    """
    print(f"Received token: {access_token}")  # Логируем полученный токен

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Убираем "Bearer " из токена если он есть
        token = access_token.replace("Bearer ", "")
        
        # Декодируем токен
        payload = jwt.decode(
            token,
            settings.ACCESS_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Получаем username из payload
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception

        # Ищем пользователя в БД
        user = await db_user.find_one_or_none(username=username)
        if not user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(f"Found user: {user.username}")
        return user

    except jwt.ExpiredSignatureError as e:
        print(f"Token expired: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        raise credentials_exception
    except Exception as e:
        # Логируем неожиданные ошибки
        print(f"Unexpected error during token validation: {str(e)}")
        print(f"Token that caused error: {token}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token validation"
        )
