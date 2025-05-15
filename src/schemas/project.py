from uuid import UUID

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from src.models import ProjectUserRole
from src.schemas.user import UserSchema


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None


class ProjectMemberCreate(BaseModel):
    email: EmailStr

class ProjectMemberResponse(UserSchema):
    role: ProjectUserRole

    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    members: List[ProjectMemberResponse]

    class Config:
        from_attributes = True 


class ProjectResponseShort(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True