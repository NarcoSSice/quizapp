import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums.action import ActionType, ActionStatus
from core.exceptions.company import NotOwnerException
from db.uow import UnitOfWork
from models import CompanyActionsModel, UserCompanyAssociation
from schemas.user import TokenUserInfoSchema
from services.action import ActionService
from tests.db.db import (
    UserFactory,
    CompanyFactory,
    ActionFactory,
    UserCompanyAssociationFactory,
)


@pytest.mark.asyncio
async def test_create_invite(
    uow: UnitOfWork, action_service: ActionService, db_session: AsyncSession
):
    owner = await UserFactory.create()
    company = await CompanyFactory.create(owner_id=owner.id)

    token_info = TokenUserInfoSchema.model_validate(owner)

    response = await action_service.create_action(
        uow,
        company_id=company.id,
        user=token_info,
        action_type=ActionType.invite,
        user_id=1,
    )

    assert response.msg == "Invite successfully sent"
    action = await db_session.execute(
        select(CompanyActionsModel).where(
            CompanyActionsModel.user_id == company.id, CompanyActionsModel.user_id == 1
        )
    )
    assert action is not None


@pytest.mark.asyncio
async def test_create_request(uow: UnitOfWork, action_service: ActionService):
    user = await UserFactory.create()

    token_info = TokenUserInfoSchema.model_validate(user)

    response = await action_service.create_action(
        uow, company_id=1, user=token_info, action_type=ActionType.request
    )

    assert response.msg == "Request successfully sent"


@pytest.mark.asyncio
async def test_create_invite_not_owner(uow: UnitOfWork, action_service: ActionService):
    owner = await UserFactory.create()
    company = await CompanyFactory.create(owner_id=owner.id)

    not_owner = await UserFactory.create()
    not_owner_token = TokenUserInfoSchema.model_validate(not_owner)

    try:
        await action_service.create_action(
            uow,
            company_id=company.id,
            user=not_owner_token,
            action_type=ActionType.invite,
            user_id=1,
        )
    except NotOwnerException as exc_info:
        assert exc_info.status_code == 401
        assert exc_info.detail == "User not owner this company"
    else:
        pytest.fail("NotOwnerException was expected")


@pytest.mark.asyncio
async def test_accept_action(
    uow: UnitOfWork, action_service: ActionService, db_session: AsyncSession
):
    user = await UserFactory.create()
    company = await CompanyFactory.create(owner_id=user.id)

    action = await ActionFactory.create(user_id=1, company_id=company.id)

    response = await action_service.accept_action(uow, action_id=action.id)
    assert response.msg == "Action successfully accepted"

    db_action = await db_session.get(CompanyActionsModel, action.id)
    assert db_action is not None
    assert db_action.status == ActionStatus.accepted


@pytest.mark.asyncio
async def test_accept_action(
    uow: UnitOfWork, action_service: ActionService, db_session: AsyncSession
):
    user = await UserFactory.create()
    company = await CompanyFactory.create(owner_id=user.id)

    action = await ActionFactory.create(user_id=1, company_id=company.id)

    response = await action_service.decline_action(uow, action_id=action.id)
    assert response.msg == "Action successfully declined"

    db_action = await db_session.get(CompanyActionsModel, action.id)
    assert db_action is not None
    assert db_action.status == ActionStatus.declined


@pytest.mark.asyncio
async def test_kick_user(
    uow: UnitOfWork, action_service: ActionService, db_session: AsyncSession
):
    owner = await UserFactory.create()
    owner_token = TokenUserInfoSchema.model_validate(owner)

    company = await CompanyFactory.create(owner_id=owner.id)
    member = await UserFactory.create()

    await UserCompanyAssociationFactory.create(user_id=member.id, company_id=company.id)

    result = await action_service.kick_user(
        uow, user_id=member.id, company_id=company.id, user=owner_token
    )

    assert result.msg == "User successfully kicked from company"

    association = await db_session.scalar(
        select(UserCompanyAssociation).where(
            UserCompanyAssociation.user_id == member.id,
            UserCompanyAssociation.company_id == company.id,
        )
    )
    assert association is None


@pytest.mark.asyncio
async def test_leave_company(
    uow: UnitOfWork, action_service: ActionService, db_session: AsyncSession
):
    member = await UserFactory.create()
    member_token = TokenUserInfoSchema.model_validate(member)

    await UserCompanyAssociationFactory.create(user_id=member.id, company_id=1)

    result = await action_service.leave_company(uow, company_id=1, user=member_token)

    assert result.msg == "You leave the company"

    association = await db_session.scalar(
        select(UserCompanyAssociation).where(
            UserCompanyAssociation.user_id == member.id,
            UserCompanyAssociation.company_id == 1,
        )
    )
    assert association is None
