from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: UUID
    username: str
    name: str
    email: str
    created_at: datetime
