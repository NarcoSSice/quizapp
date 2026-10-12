from sqlalchemy import Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models.base import Base, IDMixin


class QuizModel(Base, IDMixin):
    __tablename__ = "quizzes"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )

    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel", back_populates="quizzes"
    )
    questions: Mapped[list["QuestionModel"]] = relationship(
        "QuestionModel", back_populates="quiz", cascade="all, delete"
    )
    results: Mapped[list["QuizResultModel"]] = relationship(
        "QuizResultModel", back_populates="quiz", cascade="all, delete"
    )


class QuestionModel(Base, IDMixin):
    __tablename__ = "questions"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    quiz_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), index=True
    )

    quiz: Mapped["QuizModel"] = relationship("QuizModel", back_populates="questions")
    answers: Mapped[list["AnswerModel"]] = relationship(
        "AnswerModel", back_populates="question", cascade="all, delete"
    )


class AnswerModel(Base, IDMixin):
    __tablename__ = "answers"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), index=True
    )

    question = relationship("QuestionModel", back_populates="answers")
