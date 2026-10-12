from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, IDMixin, TimestampMixin


class UserModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    second_name: Mapped[str] = mapped_column(String(50), nullable=False)
    about: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)

    companies: Mapped[list["CompanyModel"]] = relationship(
        secondary="user_company_association",
        back_populates="members",
        overlaps="company, user",
    )
    actions: Mapped[list["CompanyActionsModel"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    quiz_results: Mapped[list["QuizResultModel"]] = relationship(
        "QuizResultModel", back_populates="user", cascade="all, delete"
    )
    company_associations: Mapped[list["UserCompanyAssociation"]] = relationship(
        "UserCompanyAssociation",
        back_populates="user",
        cascade="all, delete",
        overlaps="companies",
    )
    notifications: Mapped[list["NotificationModel"]] = relationship(
        "NotificationModel", back_populates="user", cascade="all, delete"
    )
