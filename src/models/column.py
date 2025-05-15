from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseWithTimestamps


class Column(BaseWithTimestamps):
    __tablename__ = "columns"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)
    position: Mapped[int]
    
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="column", cascade="all, delete-orphan")
    