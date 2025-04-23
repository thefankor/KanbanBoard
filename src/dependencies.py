import jwt
from fastapi import Depends, HTTPException, status

from src.config import settings
from src.dao import UserDAO
from src.models import User
from src.service.auth import oauth2_scheme


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db_user: UserDAO = Depends()
) -> User:
    """Получение текущего пользователя из токена"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception

    user = await db_user.find_one_or_none(username=username)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user
