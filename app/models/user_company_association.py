from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.enums.company_association import RoleType
from models.base import Base


class UserCompanyAssociation(Base):
    __tablename__ = "user_company_association"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    role: Mapped[RoleType] = mapped_column(Enum(RoleType), default=RoleType.member)

    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel", back_populates="associations"
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="company_associations", foreign_keys=[user_id]
    )
