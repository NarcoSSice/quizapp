from pydantic import BaseModel

from schemas.user import UserDetailSchema


class ActionSchema(BaseModel):
    id: int
    user_id: int
    company_id: int
    action_type: str
    status: str

    class Config:
        from_attributes = True


class ActionResponseSchema(BaseModel):
    msg: str


class CompanyActionListSchema(BaseModel):
    company_id: int
    action_type: str | None = None
    status: str | None = None


class UserActionTypeSchema(BaseModel):
    action_type: str


class UserActionResponseSchema(BaseModel):
    id: int
    company_id: int
    company_name: str
    action_type: str
    status: str


class CompanyActionResponseSchema(BaseModel):
    id: int
    company_id: int
    user: UserDetailSchema
    action_type: str
    status: str

    class Config:
        from_attributes = True


class ActionPayloadSchema(BaseModel):
    company_id: int
    user_id: int


class ActionIdSchema(BaseModel):
    action_id: int
