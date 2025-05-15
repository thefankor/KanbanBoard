import jwt
from fastapi import Depends, HTTPException, status
from uuid import UUID

from src.config import settings
from src.dao import UserDAO, ProjectUserDAO, TaskDAO
from src.models import User, ProjectUserRole
from src.service.auth import oauth2_scheme
from src.dao.column import ColumnDAO



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

async def get_project_user(
        project_id: UUID,
        user: User = Depends(get_current_user),
        project_user_dao: ProjectUserDAO = Depends()
) -> User:
    """
    Проверка, что пользователь является участником указанного проекта.

    Используется как зависимость для эндпоинтов, доступных только членам проекта
    (включая пользователей с любыми ролями: viewer, member, admin, owner).

    Args:
        project_id (UUID): Идентификатор проекта.
        user (User): Аутентифицированный пользователь.
        project_user_dao (ProjectUserDAO): DAO для доступа к связям проект-пользователь.

    Returns:
        User: Пользователь, если он является участником проекта.

    Raises:
        HTTPException:
            404 — если пользователь не состоит в проекте.
    """
    project_member = await project_user_dao.check_member(project_id, user.id)
    if not project_member:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this project"
        )
    return user

async def get_project_admin_user(
        project_id: UUID,
        user: User = Depends(get_project_user),
        project_user_dao: ProjectUserDAO = Depends()
) -> User:
    """
    Проверка, что пользователь является администратором или владельцем проекта.

    Используется как зависимость для защищённых эндпоинтов, доступных только
    пользователям с ролью admin или owner.

    Args:
        project_id (UUID): Идентификатор проекта.
        user (User): Пользователь, прошедший проверку участия в проекте.
        project_user_dao (ProjectUserDAO): DAO для доступа к связям проект-пользователь.

    Returns:
        User: Пользователь с правами администратора или владельца проекта.

    Raises:
        HTTPException:
            403 — если роль пользователя недостаточна для выполнения действия.
    """
    project_member = await project_user_dao.check_member(project_id, user.id)

    if project_member.role not in [ProjectUserRole.admin, ProjectUserRole.owner]:
        raise HTTPException(
            status_code=403,
            detail="Only project owner or admin can perform this action"
        )

    return user

async def get_project_owner_user(
        project_id: UUID,
        user: User = Depends(get_project_user),
        project_user_dao: ProjectUserDAO = Depends()
) -> User:
    """
    Проверка, что пользователь является владельцем проекта.

    Используется как зависимость для защищённых эндпоинтов, доступных только
    пользователям с ролью admin или owner.

    Args:
        project_id (UUID): Идентификатор проекта.
        user (User): Пользователь, прошедший проверку участия в проекте.
        project_user_dao (ProjectUserDAO): DAO для доступа к связям проект-пользователь.

    Returns:
        User: Пользователь с правами владельца проекта.

    Raises:
        HTTPException:
            403 — если роль пользователя недостаточна для выполнения действия.
    """
    project_member = await project_user_dao.check_member(project_id, user.id)

    if project_member.role != ProjectUserRole.owner:
        raise HTTPException(
            status_code=403,
            detail="Only project owner can perform this action"
        )

    return user

async def get_current_user_by_task_id_and_check_admin(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_dao: TaskDAO = Depends(TaskDAO),
    column_dao: ColumnDAO = Depends(ColumnDAO),
    project_user_dao: ProjectUserDAO = Depends(ProjectUserDAO),
) -> User:
    task = await task_dao.find_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    column = await column_dao.find_by_id(task.column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    project_id = column.project_id
    # Проверяем, что пользователь — админ или владелец проекта
    project_user = await project_user_dao.check_member(project_id, current_user.id)
    if not project_user or project_user.role not in [ProjectUserRole.admin, ProjectUserRole.owner]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def can_change_task_column(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    task_dao: TaskDAO = Depends(TaskDAO),
    column_dao: ColumnDAO = Depends(ColumnDAO),
    project_user_dao: ProjectUserDAO = Depends(ProjectUserDAO),
) -> User:
    task = await task_dao.find_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    column = await column_dao.find_by_id(task.column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    project_id = column.project_id
    
    project_user = await project_user_dao.check_member(project_id, current_user.id)
    is_admin_or_owner = project_user and project_user.role in [ProjectUserRole.admin, ProjectUserRole.owner]
    is_assignee = task.assignee_id == current_user.id
    if not (is_admin_or_owner or is_assignee):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def get_project_admin_by_column(
    column_id: UUID,
    user: User = Depends(get_current_user),
    column_dao: ColumnDAO = Depends(ColumnDAO),
    project_user_dao: ProjectUserDAO = Depends(ProjectUserDAO)
):
    """
    Проверяет, что пользователь является админом или владельцем проекта, которому принадлежит колонка.

    Args:
        column_id (UUID): Идентификатор колонки
        user (User): Текущий пользователь
        column_dao (ColumnDAO): DAO для колонок
        project_user_dao (ProjectUserDAO): DAO для участников проекта

    Returns:
        User: Пользователь, если у него есть права

    Raises:
        HTTPException: 404 — если колонка не найдена
        HTTPException: 403 — если недостаточно прав
    """
    column = await column_dao.find_by_id(column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    project_id = column.project_id
    project_member = await project_user_dao.check_member(project_id, user.id)
    if not project_member or project_member.role not in [ProjectUserRole.admin, ProjectUserRole.owner]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user
