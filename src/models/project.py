from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseWithTimestamps
from src.models.enums import ProjectUserRole


class Project(BaseWithTimestamps):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)


class ProjectUser(BaseWithTimestamps):
    __tablename__ = "project_users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[ProjectUserRole] = mapped_column(Enum(ProjectUserRole), nullable=False)


class ProjectLog(BaseWithTimestamps):
    __tablename__ = "project_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String, nullable=False)
    info: Mapped[Optional[str]] = mapped_column(Text)
