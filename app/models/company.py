from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from models.base import Base, IDMixin, TimestampMixin


class CompanyModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    members: Mapped[list["UserModel"]] = relationship(
        secondary="user_company_association",
        back_populates="companies",
        overlaps="company, company_associations, user",
    )
    associations: Mapped[list["UserCompanyAssociation"]] = relationship(
        back_populates="company",
        cascade="all, delete",
        passive_deletes=True,
        overlaps="members,companies",
    )
    actions: Mapped[list["CompanyActionsModel"]] = relationship(
        back_populates="company", cascade="all, delete"
    )
    quizzes: Mapped[list["QuizModel"]] = relationship(
        "QuizModel", back_populates="company", cascade="all, delete"
    )
    quiz_results: Mapped[list["QuizResultModel"]] = relationship(
        "QuizResultModel", back_populates="company", cascade="all, delete"
    )
