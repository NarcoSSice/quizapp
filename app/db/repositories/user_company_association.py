from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.repositories.base import BaseRepository
from models import UserModel
from models.user_company_association import UserCompanyAssociation, RoleType


class UserCompanyAssociationRepository(BaseRepository[UserCompanyAssociation]):
    model = UserCompanyAssociation

    async def delete_association(self, association: UserCompanyAssociation):
        await self.session.delete(association)

    async def add_admin(self, user_id: int, company_id: int):
        member = await self.get_by_field(user_id=user_id, company_id=company_id)
        member.role = RoleType.admin

    async def remove_admin(self, user_id: int, company_id: int):
        member = await self.get_by_field(user_id=user_id, company_id=company_id)
        member.role = RoleType.member

    async def get_admins_list(self, company_id: int):
        admins = await self.session.execute(
            select(UserModel)
            .join(self.model, UserModel.id == self.model.user_id)
            .filter(
                self.model.company_id == company_id,
                self.model.role == RoleType.admin,
            )
        )
        return admins.scalars().all()

    async def get_all_user_companies(self, user_id: int):
        result = await self.session.execute(
            select(self.model)
            .options(selectinload(self.model.company))
            .where(self.model.user_id == user_id)
        )
        return result.scalars().all()

    async def get_all_company_members(self, company_id: int, limit: int, offset: int):
        query = (
            select(self.model)
            .options(selectinload(self.model.user))
            .where(self.model.company_id == company_id)
        )
        return await self.get_items_with_pagination(query, limit, offset)
