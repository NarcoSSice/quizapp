from typing import Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.repositories.base import BaseRepository
from models import UserModel
from models.company import CompanyModel


class CompanyRepository(BaseRepository[CompanyModel]):
    model = CompanyModel

    async def get_all_companies(
        self, limit: int, offset: int
    ) -> Tuple[list[CompanyModel], int]:
        query = select(self.model).options(selectinload(self.model.members))
        return await self.get_items_with_pagination(query, limit, offset)

    async def get_company_by_id(self, company_id: int) -> CompanyModel:
        query = (
            select(self.model)
            .where(self.model.id == company_id)
            .options(selectinload(self.model.members))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
