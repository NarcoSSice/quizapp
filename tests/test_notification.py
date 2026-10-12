import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums.notification import NotificationStatus
from db.uow import UnitOfWork
from models import NotificationModel
from schemas.user import TokenUserInfoSchema
from services.notification import NotificationService
from tests.db.db import NotificationFactory, UserFactory


@pytest.mark.asyncio
async def test_get_user_notifications(
    uow: UnitOfWork, notification_service: NotificationService
):
    user = await UserFactory.create()
    user_info = TokenUserInfoSchema.model_validate(user)
    for _ in range(5):
        await NotificationFactory.create(user_id=user.id, message="Some message")

    result = await notification_service.get_user_notifications(uow, user_info)

    assert len(result) == 5
    assert result[0].message == "Some message"


@pytest.mark.asyncio
async def test_mark_as_read(
    uow: UnitOfWork, notification_service: NotificationService, db_session: AsyncSession
):
    user = await UserFactory.create()
    notification = await NotificationFactory.create(user_id=user.id)

    result = await notification_service.mark_as_read(uow, notification.id)
    await uow.commit()
    assert result.msg == "Notification marked as read"

    result = await db_session.execute(
        select(NotificationModel).where(NotificationModel.id == notification.id)
    )
    upd_notification = result.scalar_one_or_none()
    assert upd_notification.status == NotificationStatus.read
