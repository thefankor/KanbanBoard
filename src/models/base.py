from datetime import datetime

from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class BaseWithTimestamps(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
