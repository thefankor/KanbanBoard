from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.user import User
from src.models.base import BaseWithTimestamps
from src.models.enums import ProjectUserRole


class Project(BaseWithTimestamps):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)


class ProjectUser(BaseWithTimestamps):
    __tablename__ = "project_users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    role: Mapped[ProjectUserRole] = mapped_column(Enum(ProjectUserRole))

    user: Mapped[User] = relationship("User", backref="project_links")


class ProjectLog(BaseWithTimestamps):
    __tablename__ = "project_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    task_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    type: Mapped[str] = mapped_column(String)
    info: Mapped[Optional[str]] = mapped_column(Text)
