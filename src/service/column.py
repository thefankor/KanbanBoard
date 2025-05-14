from uuid import UUID

from fastapi import Depends, HTTPException

from src.dao import ColumnDAO
from src.schemas.column import ColumnCreate, ColumnUpdate, ColumnResponseShort


class ColumnService:
    def __init__(self, column_dao: ColumnDAO = Depends()):
        self.column_dao = column_dao

    async def create(self, column: ColumnCreate, project_id: UUID) -> ColumnResponseShort:
        db_column = await self.column_dao.add(**column.model_dump(), project_id=project_id)
        return ColumnResponseShort.model_validate(db_column, from_attributes=True)

    async def get(self, column_id: UUID) -> ColumnResponseShort:
        db_column = await self.column_dao.find_by_id(column_id)
        if not db_column:
            raise HTTPException(status_code=404, detail="Column not found")
        return ColumnResponseShort.model_validate(db_column, from_attributes=True)

    async def get_by_project(self, project_id: UUID) -> list[ColumnResponseShort]:
        columns = await self.column_dao.find_all(project_id=project_id)
        return [ColumnResponseShort.model_validate(c, from_attributes=True) for c in columns]

    async def update(self, column_id: UUID, column_update: ColumnUpdate) -> ColumnResponseShort:
        db_column = await self.column_dao.update(column_id, **column_update.model_dump(exclude_unset=True))
        if not db_column:
            raise HTTPException(status_code=404, detail="Column not found")
        return ColumnResponseShort.model_validate(db_column, from_attributes=True)

    async def delete(self, column_id: UUID) -> None:
        db_column = await self.column_dao.find_by_id(column_id)
        if not db_column:
            raise HTTPException(status_code=404, detail="Column not found")
        await self.column_dao.delete(column_id)
