from src.dao.base import BaseDAO
from src.models import Task


class TaskDAO(BaseDAO):
    model = Task
