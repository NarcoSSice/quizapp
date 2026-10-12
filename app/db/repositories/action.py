from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.repositories.base import BaseRepository
from models import CompanyActionsModel, UserModel
from schemas.user import TokenUserInfoSchema


class ActionRepository(BaseRepository[CompanyActionsModel]):
    model = CompanyActionsModel

    async def get_user_actions(
        self, user: TokenUserInfoSchema, action_type: str
    ) -> list[CompanyActionsModel]:
        actions = await self.session.execute(
            select(self.model)
            .options(selectinload(self.model.company))
            .join(UserModel)
            .where(UserModel.email == user.email, self.model.action_type == action_type)
        )
        return actions.scalars().all()

    async def get_company_actions(
        self,
        company_id: int,
        action_type: str | None = None,
        status: str | None = None,
    ) -> list[CompanyActionsModel]:
        filters = dict(company_id=company_id)

        if action_type:
            filters["action_type"] = action_type

        if status:
            filters["status"] = status

        actions = await self.session.execute(
            select(self.model)
            .options(selectinload(self.model.user))
            .filter_by(**filters)
        )
        return actions.scalars().all()
