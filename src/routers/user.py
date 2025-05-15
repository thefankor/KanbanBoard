from fastapi import APIRouter, Depends
from src.dependencies import get_current_user
from src.models import User
from src.schemas.user import UserSchema

router = APIRouter(tags=["User"])


@router.get("/profile", summary="Get current user profile")
async def get_profile(
    user: User = Depends(get_current_user),
):
    """Получение профиля текущего пользователя.

    Args:
        user (User): Текущий пользователь из токена

    Returns:
        User: Модель пользователя
    """
    return UserSchema(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )
