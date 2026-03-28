from fastapi import APIRouter

from app.api.routes.auth.login import router as login_router
from app.api.routes.auth.register import router as register_router

router = APIRouter(prefix="/api/auth", tags=["auth"])
router.include_router(login_router)
router.include_router(register_router)
