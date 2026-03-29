import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.leads import router as leads_router
from app.api.routes.profile import router as profile_router
from app.api.routes.settings import router as settings_router
from app.core.config import get_settings
from app.core.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

settings = get_settings()


def _validate_startup_configuration() -> None:
    runtime_settings = get_settings()
    runtime_settings.validate_auth_configuration()

    if runtime_settings.use_supabase_auth() and get_supabase_client() is None:
        raise RuntimeError(
            "Supabase auth is enabled but the Supabase client failed to initialize. "
            "Check SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY and dependencies."
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    _validate_startup_configuration()
    logger.info("Startup configuration validation passed")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

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
