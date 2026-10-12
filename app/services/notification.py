from core.enums.notification import NotificationStatus
from db.uow import UnitOfWork
from schemas.notification import NotificationSchema, MarkNotification
from schemas.user import TokenUserInfoSchema


class NotificationService:
    @staticmethod
    async def get_user_notifications(
        uow: UnitOfWork, user_info: TokenUserInfoSchema
    ) -> list[NotificationSchema]:
        user = await uow.users.get_by_field(email=user_info.email)

        notifications = await uow.notifications.get_all(user_id=user.id)
        return [
            NotificationSchema.model_validate(notification)
            for notification in notifications
        ]

    @staticmethod
    async def mark_as_read(uow: UnitOfWork, notification_id: int) -> MarkNotification:
        await uow.notifications.update(
            notification_id, dict(status=NotificationStatus.read)
        )

        return MarkNotification(msg="Notification marked as read")
