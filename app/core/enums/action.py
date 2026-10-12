import enum


class ActionType(str, enum.Enum):
    invite = "invite"
    request = "request"


class ActionStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
