import enum


class ProjectUserRole(enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class InviteProjectUserRole(enum.Enum):
    admin = "admin"
    member = "member"
