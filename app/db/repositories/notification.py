from db.repositories.base import BaseRepository
from models import NotificationModel


class NotificationRepository(BaseRepository[NotificationModel]):
    model = NotificationModel
