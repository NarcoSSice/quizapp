from sqlalchemy import Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.enums.notification import NotificationStatus
from models.base import Base, IDMixin, TimestampMixin


class NotificationModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.unread
    )

    user = relationship(
        "UserModel", back_populates="notifications", foreign_keys=[user_id]
    )
