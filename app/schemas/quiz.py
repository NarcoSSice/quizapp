from pydantic import BaseModel, Field

from schemas.question import QuestionSchema, QuestionCreateSchema, QuestionUpdateSchema


class QuizBaseSchema(BaseModel):
    title: str
    description: str

    class Config:
        from_attributes = True


class QuizSchema(QuizBaseSchema):
    id: int
    total_attempts: int
    questions: list[QuestionSchema]

    class Config:
        from_attributes = True


class QuizCreateSchema(QuizBaseSchema):
    questions: list[QuestionCreateSchema] = Field(..., min_length=2)


class QuizUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    questions: list[QuestionUpdateSchema] | None = None

    class Config:
        from_attributes = True


class QuizAnswerSchema(BaseModel):
    question_id: int
    selected_answers: list[int]


class UserQuizAnswerSchema(BaseModel):
    answers: list[QuizAnswerSchema]


class QuizResultResponseSchema(BaseModel):
    correct_answers: int
    score: float


class AverageScoreResponseSchema(BaseModel):
    score: float
