from fastapi import APIRouter, Depends

from db.uow import UnitOfWork, get_uow
from routers.dependencies import get_current_user
from schemas.notification import NotificationSchema, MarkNotification
from schemas.user import TokenUserInfoSchema
from services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationSchema])
async def get_notifications(
    user: TokenUserInfoSchema = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    notification_service: NotificationService = Depends(),
):
    return await notification_service.get_user_notifications(uow, user)


@router.patch("/{notification_id}", response_model=MarkNotification)
async def mark_as_read(
    notification_id: int,
    uow: UnitOfWork = Depends(get_uow),
    notification_service: NotificationService = Depends(),
):
    return await notification_service.mark_as_read(uow, notification_id)
