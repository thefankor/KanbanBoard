from uuid import UUID
from fastapi import Depends, HTTPException
from typing import List, Optional
from src.dao.logs import ProjectLogDAO
from src.schemas.log import ProjectLogCreate, ProjectLogResponse

class ProjectLogService:
    def __init__(self, log_dao: ProjectLogDAO = Depends()):
        super().__init__()
        self.log_dao = log_dao

    async def get(self, log_id: UUID) -> ProjectLogResponse:
        db_log = await self.log_dao.find_by_id(log_id)
        if not db_log:
            raise HTTPException(status_code=404, detail="Log not found")
        return ProjectLogResponse.model_validate(db_log, from_attributes=True)

    async def get_by_task(self, task_id: UUID) -> List[ProjectLogResponse]:
        logs = await self.log_dao.find_all(task_id=task_id)
        return [ProjectLogResponse.model_validate(l, from_attributes=True) for l in logs]

    async def get_by_project(self, project_id: UUID) -> List[ProjectLogResponse]:
        logs = await self.log_dao.find_all(project_id=project_id)
        return [ProjectLogResponse.model_validate(l, from_attributes=True) for l in logs]

    async def add_log(
        self,
        type: str,
        project_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        info: Optional[str] = None
    ) -> ProjectLogResponse:
        """
        Быстрое добавление записи в логи (для вызова из других сервисов).
        """
        log = await self.log_dao.add(
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
            type=type,
            info=info
        )

    # await log_service.add_log(
    #     task_id=task_id,
    #     user_id=current_user.id,
    #     type="update",
    #     info="Изменено поле title"
    # )
