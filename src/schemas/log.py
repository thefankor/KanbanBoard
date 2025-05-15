from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict
import datetime

class ProjectLogCreate(BaseModel):
    project_id: Optional[UUID]
    task_id: Optional[UUID]
    user_id: Optional[UUID]
    type: str
    info: Optional[str]
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ProjectLogResponse(ProjectLogCreate):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True) 