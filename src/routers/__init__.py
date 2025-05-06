from fastapi import APIRouter
from src.routers.auth import router as auth_router
from src.routers.user import router as user_router
from src.routers.project import router as project_router


router = APIRouter(prefix="/api/v1")
router.include_router(auth_router, prefix="/auth")
router.include_router(user_router, prefix="/user")
router.include_router(project_router, prefix="/project")
