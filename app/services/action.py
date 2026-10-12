from core.exceptions.company import NotOwnerException
from core.logger import logger
from db.uow import UnitOfWork
from models.action import ActionStatus
from schemas.action import (
    ActionResponseSchema,
    CompanyActionListSchema,
    UserActionResponseSchema,
    CompanyActionResponseSchema,
)
from schemas.user import TokenUserInfoSchema
from services.company import CompanyService


class ActionService:
    def __init__(self):
        self.company_service = CompanyService()

    async def create_action(
        self,
        uow: UnitOfWork,
        company_id: int,
        user: TokenUserInfoSchema,
        action_type: str,
        user_id: int | None = None,
    ) -> ActionResponseSchema:
        async with uow:
            if action_type == "invite":
                if not await self.company_service.is_owner(uow, user, company_id):
                    raise NotOwnerException
                await uow.actions.create(
                    dict(
                        user_id=user_id, action_type=action_type, company_id=company_id
                    )
                )
                return ActionResponseSchema(msg="Invite successfully sent")

            user = await uow.users.get_by_field(email=user.email)
            await uow.actions.create(
                dict(user_id=user.id, action_type=action_type, company_id=company_id)
            )
            return ActionResponseSchema(msg="Request successfully sent")

    async def accept_action(
        self, uow: UnitOfWork, action_id: int
    ) -> ActionResponseSchema:
        async with uow:
            action = await uow.actions.get_by_field(id=action_id)
            await uow.actions.update(action_id, dict(status=ActionStatus.accepted))
            await uow.user_company_association.create(
                dict(user_id=action.user_id, company_id=action.company_id)
            )
        return ActionResponseSchema(msg="Action successfully accepted")

    async def decline_action(
        self, uow: UnitOfWork, action_id: int
    ) -> ActionResponseSchema:
        async with uow:
            await uow.actions.update(action_id, dict(status=ActionStatus.declined))
        return ActionResponseSchema(msg="Action successfully declined")

    async def cancel_action(
        self, uow: UnitOfWork, action_id: int
    ) -> ActionResponseSchema:
        async with uow:
            await uow.actions.delete(action_id)
            logger.info(f"Action deleted {action_id}")
        return ActionResponseSchema(msg="Action successfully cancelled")

    async def kick_user(
        self, uow: UnitOfWork, user_id: int, company_id: int, user: TokenUserInfoSchema
    ) -> ActionResponseSchema:
        async with uow:
            if not await self.company_service.is_owner(uow, user, company_id):
                raise NotOwnerException
            association = await uow.user_company_association.get_by_field(
                user_id=user_id, company_id=company_id
            )
            await uow.user_company_association.delete_association(association)
        return ActionResponseSchema(msg="User successfully kicked from company")

    async def leave_company(
        self, uow: UnitOfWork, company_id: int, user: TokenUserInfoSchema
    ) -> ActionResponseSchema:
        async with uow:
            user = await uow.users.get_by_field(email=user.email)
            association = await uow.user_company_association.get_by_field(
                user_id=user.id, company_id=company_id
            )
            await uow.user_company_association.delete_association(association)
        return ActionResponseSchema(msg="You leave the company")

    async def get_user_actions(
        self, uow: UnitOfWork, user: TokenUserInfoSchema, action_type: str
    ) -> list[UserActionResponseSchema]:
        async with uow:
            actions = await uow.actions.get_user_actions(user, action_type)
        return [
            UserActionResponseSchema(
                id=action.id,
                company_id=action.company.id,
                company_name=action.company.name,
                action_type=action.action_type,
                status=action.status,
            )
            for action in actions
        ]

    async def get_company_actions(
        self, uow: UnitOfWork, user: TokenUserInfoSchema, data: CompanyActionListSchema
    ) -> list[CompanyActionResponseSchema]:
        async with uow:
            if not await self.company_service.is_owner(uow, user, data.company_id):
                raise NotOwnerException
            actions = await uow.actions.get_company_actions(
                **data.model_dump(exclude_none=True)
            )
        return [
            CompanyActionResponseSchema.model_validate(action) for action in actions
        ]

    async def appoint_admin(
        self, uow: UnitOfWork, user_id: int, company_id: int, user: TokenUserInfoSchema
    ):
        async with uow:
            if not await self.company_service.is_owner(uow, user, company_id):
                raise NotOwnerException

            await uow.user_company_association.add_admin(user_id, company_id)
        return ActionResponseSchema(msg="Admin successfully added")

    async def remove_admin(
        self, uow: UnitOfWork, user_id: int, company_id: int, user: TokenUserInfoSchema
    ):
        async with uow:
            if not await self.company_service.is_owner(uow, user, company_id):
                raise NotOwnerException

            await uow.user_company_association.remove_admin(user_id, company_id)
        return ActionResponseSchema(msg="Admin successfully removed")
