from core.exceptions.company import NotOwnerException
from core.logger import logger

from db.uow import UnitOfWork
from schemas.base import PaginationSchema, DeleteResponseSchema
from schemas.company import (
    CompanyCreateSchema,
    CompanyInfoSchema,
    CompanyUpdateSchema,
    CompanyWithUsersSchema,
    CompanyUserSchema,
)
from schemas.user import TokenUserInfoSchema, UserDetailSchema


class CompanyService:
    async def is_owner(
        self, func_uow: UnitOfWork, owner: TokenUserInfoSchema, company_id: int
    ) -> bool:
        user = await func_uow.users.get_by_field(email=owner.email)
        company = await func_uow.companies.get_by_field(id=company_id)
        return user.id == company.owner_id

    async def create_company(
        self,
        uow: UnitOfWork,
        company_data: CompanyCreateSchema,
        user: TokenUserInfoSchema,
    ) -> CompanyInfoSchema:
        async with uow:
            user = await uow.users.get_by_field(email=user.email)
            data = company_data.model_dump()
            data["owner_id"] = user.id
            company = await uow.companies.create(data)
            await uow.session.flush()
            await uow.user_company_association.create(
                dict(company_id=company.id, user_id=user.id, role="owner")
            )
            return CompanyInfoSchema.model_validate(company)

    async def get_all_companies(
        self, uow: UnitOfWork, limit: int, offset: int
    ) -> PaginationSchema:
        async with uow:
            items, count = await uow.companies.get_all_companies(limit, offset)
            return PaginationSchema[CompanyWithUsersSchema](
                count=count,
                items=[
                    CompanyWithUsersSchema.model_validate(company) for company in items
                ],
            )

    async def get_company_by_id(
        self, uow: UnitOfWork, company_id: int
    ) -> CompanyInfoSchema:
        async with uow:
            company = await uow.companies.get_company_by_id(company_id)
            return CompanyWithUsersSchema.model_validate(company)

    async def update_company(
        self,
        uow: UnitOfWork,
        company_id: int,
        data: CompanyUpdateSchema,
        user: TokenUserInfoSchema,
    ) -> CompanyInfoSchema:
        async with uow:
            if not await self.is_owner(uow, user, company_id):
                raise NotOwnerException
            await uow.companies.update(company_id, data.model_dump(exclude_none=True))
            updated = await uow.companies.get_by_field(id=company_id)
            return CompanyInfoSchema.model_validate(updated)

    async def delete_company(
        self, uow: UnitOfWork, company_id: int, user: TokenUserInfoSchema
    ) -> DeleteResponseSchema:
        async with uow:
            if not await self.is_owner(uow, user, company_id):
                raise NotOwnerException
            await uow.companies.delete(company_id)
        logger.info(f"Delete company {company_id}")
        return DeleteResponseSchema(status="company deleted")

    async def get_all_company_members(
        self, uow: UnitOfWork, company_id: int, limit: int, offset: int
    ) -> PaginationSchema[CompanyUserSchema]:
        async with uow:
            items, count = await uow.user_company_association.get_all_company_members(
                company_id, limit, offset
            )
        return PaginationSchema[CompanyUserSchema](
            count=count,
            items=[CompanyUserSchema.model_validate(user) for user in items],
        )

    async def get_all_admins(
        self, uow: UnitOfWork, company_id: int
    ) -> list[UserDetailSchema]:
        async with uow:
            admins = await uow.user_company_association.get_admins_list(company_id)
            return [UserDetailSchema.model_validate(admin) for admin in admins]
