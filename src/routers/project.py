from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from src.dependencies import get_current_user, get_project_admin_user, get_project_user, get_project_owner_user
from src.models.enums import InviteProjectUserRole
from src.service.project import ProjectService
from src.schemas.project import (
    ProjectCreate,
    ProjectMemberCreate,
    ProjectResponse,
    ProjectMemberResponse, ProjectResponseShort
)
from src.models import User

router = APIRouter(prefix="", tags=["Projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(ProjectService)
):
    """Создать новый проект."""
    return await project_service.create_project(project, current_user)


@router.get("/my", response_model=list[ProjectResponseShort])
async def get_my_projects(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(ProjectService)
):
    """Получить проекты текущего пользователя."""
    return await project_service.get_my_projects(current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_members(
    project_id: UUID,
    current_user: User = Depends(get_project_user),
    project_service: ProjectService = Depends(ProjectService)
):
    """Получить информацию о проекте (для участников)."""
    return await project_service.get_project(project_id)


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
async def invite_member(
    project_id: UUID,
    member: ProjectMemberCreate,
    current_user: User = Depends(get_project_admin_user),
    project_service: ProjectService = Depends(ProjectService)
):
    """Пригласить участника в проект."""
    try:
        return await project_service.invite_member(project_id, member.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse)
async def update_member_role(
    project_id: UUID,
    user_id: UUID,
    new_role: InviteProjectUserRole,
    current_user: User = Depends(get_project_owner_user),
    project_service: ProjectService = Depends(ProjectService)
):
    """Изменить роль участника (только для владельца)."""
    try:
        return await project_service.update_member_role(project_id, user_id, new_role, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}/members/{user_id}")
async def remove_member(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_project_admin_user),
    project_service: ProjectService = Depends(ProjectService)
):
    """Удалить участника из проекта."""
    await project_service.remove_member(project_id, user_id, current_user.id)
    return {"message": "Member removed successfully"} 
