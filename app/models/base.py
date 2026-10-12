from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from datetime import datetime

Base = declarative_base()


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
