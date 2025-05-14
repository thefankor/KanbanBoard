import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseWithTimestamps


class Task(BaseWithTimestamps):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    column_id: Mapped[UUID] = mapped_column(ForeignKey("columns.id"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assignee_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    producer_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    deadline: Mapped[Optional[datetime.date]] = mapped_column(Date)
    
    column: Mapped["Column"] = relationship("Column", back_populates="tasks")
