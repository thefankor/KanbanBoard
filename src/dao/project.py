from src.dao.base import BaseDAO
from src.models import Project, BaseWithTimestamps, ProjectUser


class ProjectDAO(BaseDAO):
    model = Project


class ProjectUserDAO(BaseDAO):
    model = ProjectUser
