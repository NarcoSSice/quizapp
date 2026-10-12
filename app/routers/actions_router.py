from fastapi import APIRouter, Depends, Query, Body

from db.uow import UnitOfWork, get_uow
from routers.dependencies import get_current_user
from schemas.action import (
    ActionResponseSchema,
    CompanyActionListSchema,
    UserActionResponseSchema,
    CompanyActionResponseSchema,
    ActionPayloadSchema,
    ActionIdSchema,
)
from schemas.company import CompanyIdSchema
from schemas.user import TokenUserInfoSchema
from services.action import ActionService

router = APIRouter(
    prefix="/actions",
    tags=["Actions"],
)


@router.post("/send_invite", response_model=ActionResponseSchema)
async def send_invitation(
    data: ActionPayloadSchema,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    action_service: ActionService = Depends(),
):
    return await action_service.create_action(
        uow,
        data.company_id,
        user,
        action_type="invite",
        user_id=data.user_id,
    )


@router.post("/send_request", response_model=ActionResponseSchema)
async def send_request(
    data: CompanyIdSchema,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    action_service: ActionService = Depends(),
):
    return await action_service.create_action(
        uow, data.company_id, user, action_type="request"
    )


@router.post("/accept", response_model=ActionResponseSchema)
async def accept_action(
    data: ActionIdSchema,
    uow: UnitOfWork = Depends(get_uow),
    action_service: ActionService = Depends(),
):
    return await action_service.accept_action(uow, data.action_id)


@router.post("/decline", response_model=ActionResponseSchema)
async def decline_action(
    data: ActionIdSchema,
    uow: UnitOfWork = Depends(get_uow),
    action_service: ActionService = Depends(),
):
    return await action_service.decline_action(uow, data.action_id)


@router.post("/cancel", response_model=ActionResponseSchema)
async def cancel_action(
    data: ActionIdSchema,
    uow: UnitOfWork = Depends(get_uow),
    action_service: ActionService = Depends(),
):
    return await action_service.cancel_action(uow, data.action_id)


@router.post("/kick_user", response_model=ActionResponseSchema)
async def kick_user(
    data: ActionPayloadSchema,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    action_service: ActionService = Depends(),
):
    return await action_service.kick_user(uow, data.user_id, data.company_id, user)


@router.post("/leave_company/{company_id}")
async def leave_company(
    company_id: int,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    action_service: ActionService = Depends(),
):
    return await action_service.leave_company(uow, company_id, user)


@router.get("/user_list", response_model=list[UserActionResponseSchema])
async def get_user_actions(
    action_type: str = Query(...),
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    action_service: ActionService = Depends(),
):
    return await action_service.get_user_actions(uow, user, action_type)


@router.get("/company_list", response_model=list[CompanyActionResponseSchema])
async def get_company_actions(
    company_id: int = Query(...),
    action_type: str = Query(...),
    status: str | None = Query(None),
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    action_service: ActionService = Depends(),
):
    data = CompanyActionListSchema(
        company_id=company_id,
        action_type=action_type,
        status=status,
    )
    return await action_service.get_company_actions(uow, user, data)


@router.post("/appoint_admin")
async def appoint_admin(
    data: ActionPayloadSchema,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    action_service: ActionService = Depends(),
):
    return await action_service.appoint_admin(uow, data.user_id, data.company_id, user)


@router.post("/remove_admin")
async def remove_admin(
    data: ActionPayloadSchema,
    uow: UnitOfWork = Depends(get_uow),
    user: TokenUserInfoSchema = Depends(get_current_user),
    action_service: ActionService = Depends(),
):
    return await action_service.remove_admin(uow, data.user_id, data.company_id, user)
