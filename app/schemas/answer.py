from pydantic import BaseModel


class AnswerBaseSchema(BaseModel):
    text: str
    is_correct: bool = False


class AnswerSchema(AnswerBaseSchema):
    id: int

    class Config:
        from_attributes = True


class AnswerCreateSchema(AnswerBaseSchema):
    pass


class AnswerUpdateSchema(BaseModel):
    id: int | None = None
    text: str | None = None
    is_correct: bool | None = None

    class Config:
        from_attributes = True
