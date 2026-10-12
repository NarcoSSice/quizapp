from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.repositories.base import BaseRepository
from models import UserCompanyAssociation
from models.user import UserModel


class UserRepository(BaseRepository[UserModel]):
    model = UserModel

    async def get_all_users(
        self, limit: int, offset: int
    ) -> tuple[list[UserModel], int]:
        query = select(self.model).options(selectinload(self.model.companies))
        return await self.get_items_with_pagination(query, limit, offset)

    async def get_user_by_id(self, user_id: int) -> UserModel:
        query = (
            select(self.model)
            .where(self.model.id == user_id)
            .options(selectinload(self.model.companies))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
