from abc import ABC

from fastapi import Depends
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_async_db


class BaseDAO(ABC):
    """
    Базовый класс DAO (Data Access Object) для работы с моделями SQLAlchemy.

    Предоставляет общие асинхронные методы для выполнения операций CRUD (создание, чтение, обновление, удаление).
    Предполагается, что подклассы определяют атрибут `model`, соответствующий модели SQLAlchemy.
    """

    model = None

    def __init__(self, session: AsyncSession = Depends(get_async_db)):
        """
        Инициализация DAO с сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        self.session = session

    async def find_by_id(self, model_id: int):
        """
        Найти запись по первичному ключу `id`.

        :param model_id: ID записи.
        :return: Экземпляр модели или None, если не найден.
        """
        query = select(self.model).filter_by(id=model_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_one_or_none(self, **filter_by):
        """
        Найти одну запись по указанным фильтрам.

        :param filter_by: Параметры фильтрации как именованные аргументы.
        :return: Экземпляр модели или None.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_all(self, **filter_by):
        """
        Найти все записи, соответствующие фильтрам.

        :param filter_by: Параметры фильтрации как именованные аргументы.
        :return: Список экземпляров модели.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add(self, **data):
        """
        Добавить новую запись в таблицу.

        :param data: Данные новой записи как именованные аргументы.
        :return: Добавленный экземпляр модели.
        """
        query = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, model_id: int):
        """
        Удалить запись по ID, если она существует.

        :param model_id: ID записи.
        :return: Словарь с сообщением об успешном удалении или None, если запись не найдена.
        """
        query = select(self.model).filter_by(id=model_id)
        result = await self.session.execute(query)
        if not result.scalar_one_or_none():
            return None

        stmt = delete(self.model).filter(self.model.id == model_id)
        await self.session.execute(stmt)
        await self.session.commit()
        return {"message": "Record deleted successfully"}

    async def update(self, model_id: int, **update_data):
        """
        Обновить существующую запись по ID.

        :param model_id: ID записи.
        :param update_data: Данные для обновления как именованные аргументы.
        :return: Обновлённый экземпляр модели или None, если запись не найдена.
        """
        query = select(self.model).filter_by(id=model_id)
        result = await self.session.execute(query)
        instance = result.scalar_one_or_none()
        if not instance:
            return None

        stmt = (
            update(self.model)
            .where(self.model.id == model_id)
            .values(**update_data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().all()
