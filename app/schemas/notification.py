from datetime import datetime
from pydantic import BaseModel
from core.enums.notification import NotificationStatus


class NotificationSchema(BaseModel):
    id: int
    message: str
    status: NotificationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class MarkNotification(BaseModel):
    msg: str
