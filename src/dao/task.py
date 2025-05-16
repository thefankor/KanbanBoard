from sqlalchemy import select, and_
from typing import Optional
from datetime import date
from uuid import UUID
from src.dao.base import BaseDAO
from src.models import Task


class TaskDAO(BaseDAO):
    model = Task

    async def find_filtered(
            self,
            project_id: UUID,
            assignee_id: Optional[UUID] = None,
            producer_id: Optional[UUID] = None,
            column_id: Optional[UUID] = None,
            deadline: Optional[date] = None,
            title: Optional[str] = None
    ) -> list[Task]:
        column_ids = await self.session.execute(
            select(self.model.column_id).where(self.model.column.has(project_id=project_id))
        )
        column_ids = column_ids.scalars().all()
        filters = [Task.column_id.in_(column_ids)]

        if assignee_id:
            filters.append(Task.assignee_id == assignee_id)
        if producer_id:
            filters.append(Task.producer_id == producer_id)
        if column_id:
            filters.append(Task.column_id == column_id)
        if deadline:
            filters.append(Task.deadline == deadline)
        if title:
            filters.append(Task.title.ilike(f"%{title}%"))
        stmt = select(Task).where(and_(*filters))
        result = await self.session.execute(stmt)
        return result.scalars().all()
