from sqlalchemy import select

from src.dao.base import BaseDAO
from src.models import Column


class ColumnDAO(BaseDAO):
    model = Column

    async def find_all(self, **filter_by):
        """
        Найти все записи, соответствующие фильтрам.

        :param filter_by: Параметры фильтрации как именованные аргументы.
        :return: Список экземпляров модели.
        """
        query = select(self.model).filter_by(**filter_by).order_by("position")
        result = await self.session.execute(query)
        return result.scalars().all()
