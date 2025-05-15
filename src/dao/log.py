from src.dao.base import BaseDAO
from src.models import ProjectLog


class LogDAO(BaseDAO):
    model: ProjectLog
