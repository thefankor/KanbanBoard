from typing import Union
from uuid import UUID
from datetime import date

from fastapi import Depends, HTTPException

from src.dao import ColumnDAO, TaskDAO
from src.dao.project import ProjectDAO
from src.dao.user import UserDAO

from src.models import User

from src.schemas.project import ProjectCreate, ProjectResponse
from src.schemas.task import TaskCreate, TaskResponse, ProjectTaskResponse, TaskUpdate, TaskColumnUpdate
from src.schemas.task import ColumnResponse
from src.service.log import ProjectLogService


class TaskService:
    """
    Сервис для работы с проектами и их участниками.
    Обеспечивает создание проектов, управление участниками, обновление ролей и удаление пользователей.
    """

    def __init__(
            self,
            project_dao: ProjectDAO = Depends(),
            column_dao: ColumnDAO = Depends(),
            task_dao: TaskDAO = Depends(),
            user_dao: UserDAO = Depends(),
            log_service: ProjectLogService = Depends()
    ):
        self.log_service = log_service
        self.project_dao = project_dao
        self.column_dao = column_dao
        self.task_dao = task_dao
        self.user_dao = user_dao

    async def create(self, task: TaskCreate, user: User) -> TaskResponse:
        """
        Создаёт новую задачу.

        Args:
            task (ProjectCreate): Данные нового проекта.
            user (User): Пользователь, создающий задачу.

        Returns:
            ProjectResponse: Детальная информация о задаче.
        """

        task = await self.task_dao.add(**task.model_dump(), producer_id=user.id)
        column = await self.column_dao.find_by_id(task.column_id)

        await self.log_service.add_log(
            project_id=column.project_id,
            task_id=task.id,
            user_id=user.id,
            type="task create",
        )

        return TaskResponse.model_validate(task, from_attributes=True)

    async def get_by_project(
        self,
        project_id: UUID,
        assignee_id: UUID = None,
        producer_id: UUID = None,
        column_id: UUID = None,
        deadline: date = None,
        title: str = None
    ) -> ProjectTaskResponse:
        """
        Возвращает список всех задач в проекте, сгруппированных по колонкам с фильтрами.
        """
        project = await self.project_dao.find_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        filtered_tasks = await self.task_dao.find_filtered(
            project_id=project_id,
            assignee_id=assignee_id,
            producer_id=producer_id,
            column_id=column_id,
            deadline=deadline,
            title=title
        )

        columns = await self.project_dao.get_project_columns_with_tasks(project_id)
        column_map = {col.id: col for col in columns}
        for col in columns:
            col.tasks = []
        for task in filtered_tasks:
            if task.column_id in column_map:
                column_map[task.column_id].tasks.append(task)
        return ProjectTaskResponse(
            project_id=project_id,
            columns=[
                ColumnResponse(
                    id=column.id,
                    name=column.name,
                    position=column.position,
                    tasks=[TaskResponse.model_validate(task, from_attributes=True) for task in column_map[column.id].tasks]
                ) for column in columns
            ]
        )

    async def update(self, task_id: UUID, task_update: Union[TaskUpdate, TaskColumnUpdate], user_id: UUID) -> TaskResponse:
        """
        Обновляет существующую задачу.

        Args:
            task_id (UUID): Идентификатор задачи для обновления
            task_update (TaskUpdate | TaskColumnUpdate): Данные для обновления задачи. Все поля опциональны.

        Returns:
            TaskResponse: Обновленная задача.

        Raises:
            HTTPException: 404, если задача не найдена
        """
        task = await self.task_dao.find_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task_update.column_id and not await self.column_dao.find_by_id(task_update.column_id):
            raise HTTPException(status_code=404, detail="Column not found")

        update_data = task_update.model_dump(exclude_unset=True)
        updated_task = await self.task_dao.update(task_id, **update_data)

        column = await self.column_dao.find_by_id(updated_task.column_id)

        await self.log_service.add_log(
            project_id=column.project_id,
            task_id=task.id,
            user_id=user_id,
            type="task update",
            info=f"{str(update_data)}"
        )
        
        return TaskResponse.model_validate(updated_task, from_attributes=True)

    async def delete(self, task_id: UUID, user_id: UUID) -> None:
        """
        Удаляет задачу по id.
        """
        task = await self.task_dao.find_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        await self.task_dao.delete(task_id)
