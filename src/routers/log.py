from fastapi import APIRouter, Depends
from uuid import UUID

from src.dependencies import get_project_user, get_current_user_by_task_id_and_check_admin
from src.models import ProjectUser, User
from src.schemas.log import ProjectLogCreate, ProjectLogResponse
from src.service.log import ProjectLogService

router = APIRouter(prefix="", tags=["Logs"])

@router.get("/project/{project_id}", response_model=list[ProjectLogResponse])
async def get_logs_by_project(
    project_id: UUID,
    log_service: ProjectLogService = Depends(ProjectLogService),
    current_user: User = Depends(get_project_user),
):
    """Получить все логи по проекту."""
    return await log_service.get_by_project(project_id)

@router.get("/task/{task_id}", response_model=list[ProjectLogResponse])
async def get_logs_by_task(
    task_id: UUID,
    log_service: ProjectLogService = Depends(ProjectLogService),
    _=Depends(get_current_user_by_task_id_and_check_admin),
):
    """Получить все логи по задаче."""
    return await log_service.get_by_task(task_id)
