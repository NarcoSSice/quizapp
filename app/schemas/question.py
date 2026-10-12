from pydantic import BaseModel, Field, model_validator

from core.exceptions.quiz import CorrectAnswersException
from schemas.answer import AnswerSchema, AnswerCreateSchema, AnswerUpdateSchema


class QuestionSchema(BaseModel):
    id: int
    title: str
    answers: list[AnswerSchema]

    class Config:
        from_attributes = True


class QuestionCreateSchema(BaseModel):
    title: str
    answers: list[AnswerCreateSchema] = Field(..., min_length=2)

    @model_validator(mode="after")
    def check_at_least_one_correct(self):
        if not any(answer.is_correct for answer in self.answers):
            raise CorrectAnswersException
        return self


class QuestionUpdateSchema(BaseModel):
    id: int | None = None
    title: str | None = None
    answers: list[AnswerUpdateSchema] | None = None

    class Config:
        from_attributes = True
