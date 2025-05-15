from fastapi import APIRouter, Depends
from uuid import UUID

from src.dependencies import (
    get_project_admin_user,
    get_project_user,
    can_change_task_column,
    get_current_user_by_task_id_and_check_admin
)
from src.schemas.task import (
    TaskCreate,
    TaskResponse,
    ProjectTaskResponse,
    TaskUpdate,
    TaskColumnUpdate
)

from src.models import User
from src.service.task import TaskService

router = APIRouter(prefix="", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_project_admin_user),
    task_service: TaskService = Depends(TaskService)
):
    """Создать новую задачу."""
    return await task_service.create(task, current_user)


@router.get("/{project_id}", response_model=ProjectTaskResponse)
async def get_tasks(
    project_id: UUID,
    current_user: User = Depends(get_project_user),
    task_service: TaskService = Depends(TaskService)
):
    """Получить проекты текущего пользователя."""
    return await task_service.get_by_project(project_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user_by_task_id_and_check_admin),
    task_service: TaskService = Depends(TaskService)
):
    """Обновить существующую задачу."""
    return await task_service.update(task_id, task_update, current_user.id)


@router.patch("/{task_id}/column", response_model=TaskResponse)
async def update_task_column(
    task_id: UUID,
    column_update: TaskColumnUpdate,
    current_user: User =Depends(can_change_task_column),
    task_service: TaskService = Depends(TaskService)
):
    """Переместить задачу в другую колонку (доступно админу/владельцу или исполнителю)."""
    return await task_service.update(task_id, column_update, current_user.id)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    current_user: User =Depends(get_current_user_by_task_id_and_check_admin),
    task_service: TaskService = Depends(TaskService)
):
    """Удалить задачу (доступно админу или владельцу проекта)."""
    await task_service.delete(task_id, current_user.id)
