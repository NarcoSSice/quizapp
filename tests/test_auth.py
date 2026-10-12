import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.uow import UnitOfWork
from models import UserModel
from schemas.user import UserSignUpSchema, UserSignInSchema
from services.auth import AuthService
from tests.test_user import user_test_create_data
from utils.jwt_auth import jwt_auth


@pytest.mark.asyncio
async def test_register_user(
    uow: UnitOfWork, auth_service: AuthService, db_session: AsyncSession
):
    token = await auth_service.register_user(
        uow, UserSignUpSchema.model_validate(user_test_create_data)
    )
    decoded_token = jwt_auth.decode_token(token)
    assert decoded_token["email"] == user_test_create_data.email
    user = await db_session.execute(
        select(UserModel).where(UserModel.email == decoded_token["email"])
    )
    assert user is not None


@pytest.mark.asyncio
async def test_login_user(uow: UnitOfWork, auth_service: AuthService):
    credentials = UserSignInSchema(email="example@gmail.com", password="string")
    token = await auth_service.login_user(uow, credentials)
    decoded_token = jwt_auth.decode_token(token)
    assert decoded_token is not None
    assert decoded_token["email"] == credentials.email


@pytest.mark.asyncio
async def test_login_with_not_exist_email(uow: UnitOfWork, auth_service: AuthService):
    credentials = UserSignInSchema(email="exa@gmail.com", password="string")
    try:
        await auth_service.login_user(uow, credentials)
    except HTTPException as exc_info:
        assert exc_info.status_code == 404
        assert exc_info.detail == "User not found"
    else:
        pytest.fail("HTTPException was expected")


@pytest.mark.asyncio
async def test_login_with_wrong_password(uow: UnitOfWork, auth_service: AuthService):
    credentials = UserSignInSchema(email="example@gmail.com", password="stridaadsdang")
    try:
        await auth_service.login_user(uow, credentials)
    except HTTPException as exc_info:
        assert exc_info.status_code == 401
        assert exc_info.detail == "Incorrect password"
    else:
        pytest.fail("HTTPException was expected")
