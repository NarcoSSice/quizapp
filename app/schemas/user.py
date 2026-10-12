from pydantic import BaseModel, EmailStr, Field

from schemas.base import TimeStampSchema


class UserBaseSchema(TimeStampSchema):
    id: int
    email: EmailStr
    first_name: str = Field(max_length=50)
    second_name: str = Field(max_length=50)
    about: str | None
    image_url: str | None

    class Config:
        from_attributes = True


class UserSignInSchema(BaseModel):
    email: EmailStr
    password: str


class UserSignUpSchema(BaseModel):
    email: EmailStr
    password: str
    first_name: str = Field(max_length=50)
    second_name: str = Field(max_length=50)


class UserUpdateSchema(BaseModel):
    password: str | None = None
    first_name: str | None = None
    second_name: str | None = None
    about: str | None = None
    image_url: str | None = None

    class Config:
        extra = "forbid"


class UserDetailSchema(UserBaseSchema):
    pass


class TokenUserInfoSchema(BaseModel):
    email: EmailStr
    first_name: str = Field(max_length=50)
    second_name: str = Field(max_length=50)

    class Config:
        from_attributes = True


class UserCompanySchema(BaseModel):
    company_id: int
    company_name: str
    role: str
