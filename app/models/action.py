from sqlalchemy import Integer, ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core.enums.action import ActionType, ActionStatus
from models.base import Base, IDMixin, TimestampMixin


class CompanyActionsModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "company_actions"

    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType))
    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus), default=ActionStatus.pending
    )

    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel", back_populates="actions", foreign_keys=[company_id]
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="actions", foreign_keys=[user_id]
    )
