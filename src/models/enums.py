import enum


class ProjectUserRole(enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
