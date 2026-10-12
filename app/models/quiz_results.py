from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func, Integer, ARRAY, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, IDMixin


class QuizResultModel(Base, IDMixin):
    __tablename__ = "quiz_results"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), index=True
    )

    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    answered_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    last_attempt_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user = relationship(
        "UserModel", back_populates="quiz_results", foreign_keys=[user_id]
    )
    company = relationship(
        "CompanyModel", back_populates="quiz_results", foreign_keys=[company_id]
    )
    quiz = relationship("QuizModel", back_populates="results", foreign_keys=[quiz_id])
    responses: Mapped[list["UserQuizAnswerModel"]] = relationship(
        "UserQuizAnswerModel", back_populates="quiz_result", cascade="all, delete"
    )


class UserQuizAnswerModel(Base, IDMixin):
    __tablename__ = "user_quiz_answers"

    quiz_result_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_results.id", ondelete="CASCADE"), index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), index=True
    )

    user_answer: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    quiz_result = relationship(
        "QuizResultModel", back_populates="responses", foreign_keys=[quiz_result_id]
    )
