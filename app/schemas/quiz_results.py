from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponsesSchema(BaseModel):
    question_id: int
    user_answer: list[int]
    is_correct: bool

    class Config:
        from_attributes = True


class ResultAnswersResponseSchema(BaseModel):
    user_email: EmailStr
    company_name: str
    quiz_title: str
    total_questions: int
    answered_questions: int
    correct_answers: int
    responses: list[UserResponsesSchema]

    class Config:
        from_attributes = True


class CompanyExportQuizResultsSchema(BaseModel):
    user_email: EmailStr
    company_name: str
    quiz_title: str
    total_questions: int
    answered_questions: int
    correct_answers: int


class AnalyticsResponseBaseSchema(BaseModel):
    quiz_id: int
    quiz_title: str


class UserQuizAverageScoresSchema(AnalyticsResponseBaseSchema):
    score: float
    first_taken: datetime
    last_taken: datetime


class UserQuizzesLastCompletionsSchema(AnalyticsResponseBaseSchema):
    last_attempt: datetime


class CompanyAverageByWeekSchema(BaseModel):
    week: datetime
    score: float


class UserQuizScoresSchema(AnalyticsResponseBaseSchema):
    week: datetime
    score: float


class CompanyUsersScoresByWeekSchema(AnalyticsResponseBaseSchema):
    week: datetime
    score: float


class CompanyUsersLastAttemptSchema(BaseModel):
    user_email: EmailStr
    last_attempt: datetime
