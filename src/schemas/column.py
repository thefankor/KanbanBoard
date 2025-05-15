from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ColumnCreate(BaseModel):
    name: str
    position: int
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ColumnUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ColumnResponseShort(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    position: int
    model_config = ConfigDict(from_attributes=True) 