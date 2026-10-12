from datetime import datetime
from pydantic import BaseModel


class TimeStampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class PaginationSchema[ListSchemas](BaseModel):
    count: int
    items: list[ListSchemas]


class DeleteResponseSchema(BaseModel):
    status: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class ResponseSchema(BaseModel):
    msg: str
