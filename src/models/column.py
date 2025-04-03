from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseWithTimestamps


class Column(BaseWithTimestamps):
    __tablename__ = "columns"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    