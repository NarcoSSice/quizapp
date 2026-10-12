from fastapi import APIRouter, Depends, Query

from core.constants import COMPANY_ROUTE, COMPANY_ID_ROUTE
from db.uow import UnitOfWork, get_uow
from routers.dependencies import get_current_user
from schemas.base import PaginationSchema, DeleteResponseSchema
from schemas.company import (
    CompanyCreateSchema,
    CompanyInfoSchema,
    CompanyUpdateSchema,
    CompanyWithUsersSchema,
    CompanyUserSchema,
)
from schemas.user import TokenUserInfoSchema, UserDetailSchema
from services.company import CompanyService

router = APIRouter(
    prefix=COMPANY_ROUTE,
    tags=["Companies"],
)


@router.post("/", response_model=CompanyInfoSchema)
async def create_company(
    company_data: CompanyCreateSchema,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    company_service: CompanyService = Depends(),
):
    return await company_service.create_company(uow, company_data, user)


@router.get("/", response_model=PaginationSchema[CompanyWithUsersSchema])
async def get_all_companies(
    uow: UnitOfWork = Depends(get_uow),
    company_service: CompanyService = Depends(),
    limit: int = Query(10, ge=0),
    offset: int = Query(0, ge=0),
):
    return await company_service.get_all_companies(uow, limit, offset)


@router.get(COMPANY_ID_ROUTE, response_model=CompanyWithUsersSchema)
async def get_company(
    company_id: int,
    uow: UnitOfWork = Depends(get_uow),
    company_service: CompanyService = Depends(),
):
    return await company_service.get_company_by_id(uow, company_id)


@router.patch(COMPANY_ID_ROUTE, response_model=CompanyInfoSchema)
async def update_company(
    company_id: int,
    update_data: CompanyUpdateSchema,
    uow: UnitOfWork = Depends(get_uow),
    owner: TokenUserInfoSchema = Depends(get_current_user),
    company_service: CompanyService = Depends(),
):
    return await company_service.update_company(uow, company_id, update_data, owner)


@router.delete(COMPANY_ID_ROUTE, response_model=DeleteResponseSchema)
async def delete_company(
    company_id: int,
    uow: UnitOfWork = Depends(get_uow),
    owner: TokenUserInfoSchema = Depends(get_current_user),
    company_service: CompanyService = Depends(),
):
    return await company_service.delete_company(uow, company_id, owner)


@router.get(
    f"{COMPANY_ID_ROUTE}/members", response_model=PaginationSchema[CompanyUserSchema]
)
async def get_all_members(
    company_id: int,
    company_service: CompanyService = Depends(),
    uow: UnitOfWork = Depends(get_uow),
    limit: int = Query(10, ge=0),
    offset: int = Query(0, ge=0),
):
    return await company_service.get_all_company_members(uow, company_id, limit, offset)


@router.get(f"{COMPANY_ID_ROUTE}/admins", response_model=list[UserDetailSchema])
async def get_all_admins(
    company_id: int,
    uow: UnitOfWork = Depends(get_uow),
    company_service: CompanyService = Depends(),
):
    return await company_service.get_all_admins(uow, company_id)
