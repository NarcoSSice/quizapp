import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.uow import UnitOfWork
from models.user import UserModel
from schemas.base import PaginationSchema
from schemas.user import UserDetailSchema, UserUpdateSchema, UserSignUpSchema
from services.user import UserService
from tests.conftest import user_data
from tests.test_company import user_token_data

user_test_create_data = UserSignUpSchema(
    email="example333@gmail.com",
    password="string",
    first_name="string",
    second_name="string",
)


@pytest.mark.asyncio
async def test_create_user(
    uow: UnitOfWork, user_service: UserService, db_session: AsyncSession
):
    response = await user_service.create_user(uow, user_test_create_data)
    assert isinstance(response, UserDetailSchema)
    assert response.email == user_test_create_data.email
    user = await db_session.execute(
        select(UserModel).where(UserModel.email == user_test_create_data.email)
    )
    assert user is not None


@pytest.mark.asyncio
async def test_create_exist_user(uow: UnitOfWork, user_service: UserService):
    try:
        user_test_create_data.email = "example@gmail.com"
        await user_service.create_user(uow, user_test_create_data)
    except HTTPException as exc_info:
        assert exc_info.status_code == 404
        assert exc_info.detail == "User with this email already exist"
    else:
        pytest.fail("HTTPException was expected")


@pytest.mark.asyncio
async def test_get_user_by_id(uow: UnitOfWork, user_service: UserService):
    user = await user_service.get_user_by_id(uow, 1)
    assert user is not None
    assert user.email == user_data.email


@pytest.mark.asyncio
async def test_get_user_with_not_exist_id(uow: UnitOfWork, user_service: UserService):
    try:
        await user_service.get_user_by_id(uow, 100)
    except HTTPException as exc_info:
        assert exc_info.status_code == 404
        assert exc_info.detail == "User not found"
    else:
        pytest.fail("HTTPException was expected")


@pytest.mark.asyncio
async def test_update_user(uow: UnitOfWork, user_service: UserService):
    update_data = UserUpdateSchema(first_name="stringsssssssss", second_name="ssdada")
    user = await user_service.update_user(uow, 1, update_data)
    assert user is not None
    assert isinstance(user, UserDetailSchema)
    assert user.first_name == update_data.first_name
    assert user.second_name == update_data.second_name


@pytest.mark.asyncio
async def test_get_all_users(uow: UnitOfWork, user_service: UserService):
    response = await user_service.get_all_users(uow, limit=10, offset=0)
    assert isinstance(response, PaginationSchema)
    assert len(response.items) <= 10
    assert len(response.items) == response.count


@pytest.mark.asyncio
async def test_delete_user(uow: UnitOfWork, user_service: UserService):
    response = await user_service.delete_user(uow, 1, user_token_data)
    assert response.status == "user deleted"
