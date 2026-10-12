import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.uow import UnitOfWork
from models import CompanyModel
from schemas.base import PaginationSchema
from schemas.company import CompanyCreateSchema, CompanyInfoSchema, CompanyUpdateSchema
from schemas.user import TokenUserInfoSchema
from services.company import CompanyService
from tests.conftest import company_data, user_data

company_test_create_data = CompanyCreateSchema(
    name="Test Company", description="Some description", is_hidden=True
)

user_token_data = TokenUserInfoSchema.model_validate(user_data)


@pytest.mark.asyncio
async def test_create_company(
    uow: UnitOfWork, company_service: CompanyService, db_session: AsyncSession
):
    response = await company_service.create_company(
        uow, company_test_create_data, user_token_data
    )
    assert isinstance(response, CompanyInfoSchema)
    company = await db_session.execute(
        select(CompanyModel).where(CompanyModel.name == company_test_create_data.name)
    )
    assert company is not None


@pytest.mark.asyncio
async def test_get_all_companies(uow: UnitOfWork, company_service: CompanyService):
    response = await company_service.get_all_companies(uow, limit=10, offset=0)
    assert isinstance(response, PaginationSchema)
    assert len(response.items) <= 10
    assert len(response.items) == response.count


@pytest.mark.asyncio
async def test_get_company_by_id(uow: UnitOfWork, company_service: CompanyService):
    company = await company_service.get_company_by_id(uow, 1)
    assert company is not None
    assert company.name == company_data.name


@pytest.mark.asyncio
async def test_update_company(uow: UnitOfWork, company_service: CompanyService):
    update_data = CompanyUpdateSchema(
        name="Test Company",
        description="Some description",
    )
    company = await company_service.update_company(uow, 1, update_data, user_token_data)
    assert company is not None
    assert company.name == update_data.name
    assert company.description == update_data.description


@pytest.mark.asyncio
async def test_delete_company(uow: UnitOfWork, company_service: CompanyService):
    response = await company_service.delete_company(uow, 1, user_token_data)
    assert response.status == "company deleted"
