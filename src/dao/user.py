from src.dao.base import BaseDAO
from src.models import User


class UserDAO(BaseDAO):
    model = User
