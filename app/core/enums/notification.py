import enum


class NotificationStatus(str, enum.Enum):
    read = "read"
    unread = "unread"
