from uuid import UUID

from fastapi import Depends, HTTPException, status
from pydantic import EmailStr

from src.dao import ColumnDAO
from src.dao.project import ProjectDAO, ProjectUserDAO
from src.dao.user import UserDAO

from src.models import User
from src.models.enums import InviteProjectUserRole
from src.models.project import ProjectUserRole, Project

from src.schemas.project import ProjectCreate, ProjectResponse, ProjectMemberResponse, \
    ProjectResponseShort


class ProjectService:
    """
    Сервис для работы с проектами и их участниками.
    Обеспечивает создание проектов, управление участниками, обновление ролей и удаление пользователей.
    """

    def __init__(
            self,
             project_dao: ProjectDAO = Depends(),
             project_user_dao: ProjectUserDAO = Depends(),
             column_dao: ColumnDAO = Depends(),
             user_dao: UserDAO = Depends()
             ):
        self.project_dao = project_dao
        self.project_user_dao = project_user_dao
        self.column_dao = column_dao
        self.user_dao = user_dao

    async def create_project(self, project: ProjectCreate, owner: User) -> ProjectResponse:
        """
        Создаёт новый проект и добавляет текущего пользователя как владельца.

        Args:
            project (ProjectCreate): Данные нового проекта.
            owner (User): Пользователь, создающий проект.

        Returns:
            ProjectResponse: Детальная информация о проекте с владельцем.
        """

        db_project = await self.project_dao.create_project(project)

        await self.create_default_columns(db_project)

        db_member = await self.project_user_dao.add_project_member(
                project_id=db_project.id,
                user_id=owner.id,
                role=ProjectUserRole.owner
        )
        return ProjectResponse(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at,
            members=[
                ProjectMemberResponse(
                    id=db_member.user_id,
                    username=owner.username,
                    name=owner.name,
                    email=owner.email,
                    role=db_member.role,
                    created_at=db_member.created_at,
                )
            ]
        )

    async def create_default_columns(self, project: Project):
        """
        Создает стандартные колонки для указанного проекта.

        По умолчанию создаются следующие колонки:
        - "Backlog"
        - "Doing"
        - "Review"
        - "Done"

        Каждая колонка создается с позицией, соответствующей порядковому номеру в списке.

        Args:
            project (Project): Экземпляр проекта, для которого создаются колонки.

        Returns:
            None
        """
        default_columns = ["Backlog", "Doing", "Review", "Done"]
        for idx, column_name in enumerate(default_columns):
            await self.column_dao.add(
                project_id=project.id,
                name=column_name,
                position=idx
            )

    async def invite_member(self, project_id: UUID, email: EmailStr) -> ProjectMemberResponse:
        """
        Приглашает пользователя в проект по email.

        Args:
            project_id (UUID): Идентификатор проекта.
            email (EmailStr): Email пользователя для приглашения.

        Returns:
            ProjectMemberResponse: Информация о приглашённом участнике.

        Raises:
            ValueError: Если проект или пользователь не найден, либо пользователь уже состоит в проекте.
        """

        project = await self.project_dao.find_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        
        user = await self.user_dao.find_one_or_none(email=email)
        if not user:
            raise ValueError("User not found")

        existing_member = await self.project_user_dao.check_member(
            project_id=project_id,
            user_id=user.id
        )
        if existing_member:
            raise ValueError("User is already a member of this project")

        project_user = await self.project_user_dao.add_project_member(
            project_id=project_id,
            user_id=user.id,
        )

        return ProjectMemberResponse(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            role=project_user.role,
            created_at=user.created_at,
        )

    async def get_my_projects(self, user_id: UUID) -> list[ProjectResponseShort]:
        """
        Возвращает список всех проектов, в которых участвует пользователь.

        Args:
            user_id (UUID): Идентификатор пользователя.

        Returns:
            list[ProjectResponseShort]: Список проектов с краткой информацией.
        """

        projects = await self.project_dao.get_projects_by_user(user_id=user_id)
        return [ProjectResponseShort.model_validate(p) for p in projects]

    async def get_project(self, project_id: UUID) -> ProjectResponse:
        """
        Возвращает полную информацию о проекте, включая участников.

        Args:
            project_id (UUID): Идентификатор проекта.

        Returns:
            ProjectResponse: Детальная информация о проекте и его участниках.

        Raises:
            HTTPException: 404, если проект не найден.
        """

        project = await self.project_dao.find_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        members = await self.project_user_dao.get_project_members(project_id=project_id)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            members=members
        )

    async def update_member_role(
            self,
            project_id: UUID,
            user_id: UUID,
            new_role: InviteProjectUserRole,
            current_user_id: UUID
    ) -> ProjectMemberResponse:
        """
        Обновляет роль участника проекта.

        Args:
            project_id (UUID): Идентификатор проекта.
            user_id (UUID): Идентификатор участника, чья роль обновляется.
            new_role (InviteProjectUserRole): Новая роль для участника.
            current_user_id (UUID): Идентификатор текущего пользователя (должен быть владельцем).

        Returns:
            ProjectMemberResponse: Обновлённая информация об участнике.

        Raises:
            HTTPException: 403, если пользователь пытается изменить собственную роль.
        """

        if user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project owner cannot change their own role"
            )
        await self.project_user_dao.update_role(project_id, user_id, new_role.name)
        user = await self.user_dao.find_by_id(user_id)
        return ProjectMemberResponse(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            role=new_role.name,
        )

    async def remove_member(
            self,
            project_id: UUID,
            user_id: UUID,
            current_user_id: UUID,
    ) -> bool:
        """
        Удаляет участника из проекта с учётом прав доступа.

        Владельцы могут удалять любых участников (кроме себя).
        Администраторы могут удалять только пользователей с ролью `member`.

        Args:
            project_id (UUID): Идентификатор проекта.
            user_id (UUID): Идентификатор удаляемого участника.
            current_user_id (UUID): Идентификатор текущего пользователя.

        Returns:
            bool: True, если участник успешно удалён.

        Raises:
            HTTPException:
                403 — если текущий пользователь не имеет прав удалить участника.
                404 — если участник не найден.
        """

        project_user = await self.project_user_dao.find_one_or_none(project_id=project_id, user_id=user_id)
        current_project_user = await self.project_user_dao.find_one_or_none(project_id=project_id,
                                                                            user_id=current_user_id)

        if not project_user:
            raise HTTPException(status_code=404, detail="Member not found")

        if user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot remove yourself from the project"
            )

        if current_project_user.role == ProjectUserRole.owner:
            await self.project_user_dao.remove_project_member(project_id, user_id)
            return True

        if current_project_user.role == ProjectUserRole.admin:
            if project_user.role in [ProjectUserRole.member]:
                await self.project_user_dao.remove_project_member(project_id, user_id)
                return True
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admins cannot remove other admins or the owner"
                )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to remove this member"
        )
