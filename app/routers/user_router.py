from fastapi import APIRouter, Depends, Query

from db.uow import UnitOfWork, get_uow
from routers.dependencies import get_current_user
from schemas.base import PaginationSchema, DeleteResponseSchema
from schemas.company import UserWithCompaniesSchema
from schemas.user import (
    UserDetailSchema,
    UserSignUpSchema,
    UserUpdateSchema,
    UserCompanySchema,
    TokenUserInfoSchema,
)
from services.user import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=PaginationSchema[UserWithCompaniesSchema])
async def get_users(
    user_service: UserService = Depends(),
    limit: int = Query(10, ge=0),
    offset: int = Query(0, ge=0),
    uow: UnitOfWork = Depends(get_uow),
):
    return await user_service.get_all_users(uow, limit, offset)


@router.post("/", response_model=UserDetailSchema)
async def create_user(
    data: UserSignUpSchema,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(),
):
    return await user_service.create_user(uow, data)


@router.get("/{user_id}", response_model=UserWithCompaniesSchema)
async def get_user(
    user_id: int,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(),
):
    return await user_service.get_user_by_id(uow, user_id)


@router.put("/{user_id}", response_model=UserDetailSchema)
async def update_user(
    user_id: int,
    data: UserUpdateSchema,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(),
):
    return await user_service.update_user(uow, user_id, data)


@router.delete("/{user_id}", response_model=DeleteResponseSchema)
async def delete_user(
    user_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: TokenUserInfoSchema = Depends(get_current_user),
    user_service: UserService = Depends(),
):
    return await user_service.delete_user(uow, user_id, current_user)


@router.get("/{user_id}/companies", response_model=list[UserCompanySchema])
async def get_all_user_companies(
    user_id: int,
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(),
):
    return await user_service.get_all_user_companies(uow, user_id)
