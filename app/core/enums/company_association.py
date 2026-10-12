import enum


class RoleType(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
