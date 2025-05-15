from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.dao.base import BaseDAO
from src.models import Project, ProjectUser, ProjectUserRole, Column, Task
from src.schemas.project import ProjectCreate, ProjectMemberCreate, ProjectMemberResponse


class ProjectDAO(BaseDAO):
    model = Project

    async def create_project(self, project: ProjectCreate) -> Project:
        return await self.add(
            name=project.name,
            description=project.description
        )

    async def get_projects_by_user(self, user_id: UUID) -> list[Project]:
        stmt = (
            select(Project)
            .join(ProjectUser, Project.id == ProjectUser.project_id)
            .where(ProjectUser.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_project_columns_with_tasks(self, project_id: UUID) -> list[Column]:
        """
        Получает все колонки проекта вместе с их задачами.
        
        Args:
            project_id (UUID): Идентификатор проекта
            
        Returns:
            list[Column]: Список колонок с их задачами
        """
        stmt = (
            select(Column)
            .where(Column.project_id == project_id)
            .options(joinedload(Column.tasks))
            .order_by(Column.position)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()


class ProjectUserDAO(BaseDAO):
    model = ProjectUser

    async def add_project_member(
            self,
            project_id: UUID,
            user_id: UUID,
            role: Optional[ProjectUserRole] = None
    ) -> ProjectUser:
        return await self.add(
            project_id=project_id,
            user_id=user_id,
            role=role if role else ProjectUserRole.member
        )

    async def check_member(self, project_id: UUID, user_id: UUID) -> Optional[ProjectUser]:
        return await self.find_one_or_none(
            project_id=project_id,
            user_id=user_id
        )

    async def get_project_members(self, project_id: UUID) -> List[ProjectMemberResponse]:
        """
        Получает список всех участников проекта с их ролями.

        Args:
            project_id (UUID): Идентификатор проекта.

        Returns:
            List[ProjectMemberResponse]: Список участников проекта с ролями.
        """
        stmt = (
            select(ProjectUser)
            .options(joinedload(ProjectUser.user))  # загрузка связанных пользователей
            .where(ProjectUser.project_id == project_id)
        )

        result = await self.session.execute(stmt)
        project_users = result.scalars().all()

        # Формируем ответ в формате схемы ProjectMemberResponse
        return [
            ProjectMemberResponse.model_validate(
                {
                    **vars(pu.user),
                    "role": pu.role,
                }
            )
            for pu in project_users
        ]

    async def update_role(self, project_id: UUID, user_id: UUID, new_role: str) -> ProjectUser:
        member = await self.find_one_or_none(project_id=project_id, user_id=user_id)
        if not member:
            raise ValueError("Member not found")
        return await self.update(member.id, role=new_role)

    async def remove_project_member(self, project_id: UUID, user_id: UUID) -> bool:
        member = await self.find_one_or_none(project_id=project_id, user_id=user_id)
        if not member:
            return False
        await self.delete(member.id)
        return True
