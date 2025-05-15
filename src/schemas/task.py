import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    column_id: UUID
    title: str
    description: Optional[str]
    deadline: Optional[datetime.date] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TaskUpdate(BaseModel):
    column_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime.date] = None
    assignee_id: Optional[UUID] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TaskResponse(TaskCreate):
    id: UUID
    assignee_id: Optional[UUID]
    producer_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True  # Это позволяет работать с ORM моделями
    )


class ColumnResponse(BaseModel):
    id: UUID
    name: str
    position: int
    tasks: list[TaskResponse]


class ProjectTaskResponse(BaseModel):
    project_id: UUID
    columns: list[ColumnResponse]


class TaskColumnUpdate(BaseModel):
    column_id: UUID
    model_config = ConfigDict(arbitrary_types_allowed=True)

# class ProjectUpdate(ProjectBase):
#     name: Optional[str] = None