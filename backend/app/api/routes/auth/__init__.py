from fastapi import APIRouter

from app.api.routes.auth.login import router as login_router
from app.api.routes.auth.logout import router as logout_router
from app.api.routes.auth.register import router as register_router
from app.api.routes.auth.session import router as session_router

router = APIRouter(prefix="/api/auth", tags=["auth"])
router.include_router(login_router)
router.include_router(register_router)
router.include_router(session_router)
router.include_router(logout_router)
