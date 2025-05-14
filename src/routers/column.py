from fastapi import APIRouter, Depends
from uuid import UUID

from src.dependencies import (
    get_project_admin_user,
    get_project_user,
    get_project_admin_by_column,
)
from src.schemas.column import ColumnCreate, ColumnUpdate, ColumnResponseShort

from src.models import User
from src.service.column import ColumnService

router = APIRouter(prefix="/column", tags=["Columns"])


@router.get("/project/{project_id}", response_model=list[ColumnResponseShort])
async def get_columns_by_project(
    project_id: UUID,
    current_user: User = Depends(get_project_user),
    column_service: ColumnService = Depends(ColumnService)
):
    """Получить все колонки по project_id."""
    return await column_service.get_by_project(project_id)


@router.post("/", response_model=ColumnResponseShort, status_code=201)
async def create_column(
    column: ColumnCreate,
    project_id: UUID,
    current_user: User = Depends(get_project_admin_user),
    column_service: ColumnService = Depends(ColumnService)
):
    """Создать новую колонку."""
    return await column_service.create(column, project_id)


@router.patch("/{column_id}", response_model=ColumnResponseShort)
async def update_column(
    column_id: UUID,
    column_update: ColumnUpdate,
    current_user: User = Depends(get_project_admin_by_column),
    column_service: ColumnService = Depends(ColumnService)
):
    """Обновить колонку."""
    return await column_service.update(column_id, column_update)


@router.delete("/{column_id}", status_code=204)
async def delete_column(
    column_id: UUID,
    current_user: User = Depends(get_project_admin_by_column),
    column_service: ColumnService = Depends(ColumnService)
):
    """Удалить колонку."""
    await column_service.delete(column_id)
