from pydantic import BaseModel

from core.enums.company_association import RoleType
from schemas.base import TimeStampSchema
from schemas.user import UserDetailSchema, UserBaseSchema


class CompanyCreateSchema(BaseModel):
    name: str
    description: str | None = None
    is_hidden: bool


class CompanyInfoSchema(TimeStampSchema):
    id: int
    name: str
    description: str | None
    is_hidden: bool
    owner_id: int

    class Config:
        from_attributes = True


class CompanyUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    is_hidden: bool | None = None


class CompanyIdSchema(BaseModel):
    company_id: int


class CompanyUserSchema(BaseModel):
    user: UserDetailSchema
    role: RoleType

    class Config:
        from_attributes = True


class CompanyWithUsersSchema(CompanyInfoSchema):
    members: list[UserDetailSchema]

    class Config:
        from_attributes = True


class UserWithCompaniesSchema(UserBaseSchema):
    companies: list[CompanyInfoSchema]

    class Config:
        from_attributes = True
