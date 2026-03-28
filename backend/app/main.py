from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.leads import router as leads_router
from app.api.routes.profile import router as profile_router
from app.api.routes.settings import router as settings_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(profile_router)
app.include_router(leads_router)
app.include_router(settings_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "F1bot API is running."}
