import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.leads import router as leads_router
from app.api.routes.profile import router as profile_router
from app.api.routes.settings import router as settings_router
from app.core.config import get_settings
from app.core.scan_limits import validate_auth_limits_startup_configuration
from app.core.supabase_client import get_supabase_auth_client

logger = logging.getLogger(__name__)

settings = get_settings()


def _validate_startup_configuration() -> None:
    runtime_settings = get_settings()
    runtime_settings.validate_auth_configuration()
    validate_auth_limits_startup_configuration()

    if runtime_settings.use_supabase_auth() and get_supabase_auth_client() is None:
        raise RuntimeError(
            "Supabase auth is enabled but the Supabase client failed to initialize. "
            "Check SUPABASE_URL/SUPABASE_ANON_KEY and dependencies."
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    _validate_startup_configuration()
    logger.info("Startup configuration validation passed")
    yield


# Endpoints whose user_id comes from the Bearer token, not a query param.
_PROTECTED_OPERATION_IDS: set[str] = {
    "get_profile_api_profile_get",
    "upsert_profile_api_profile_put",
    "scan_leads_api_leads_scan_post",
    "list_leads_api_leads_get",
    "export_leads_csv_api_leads_export_csv_get",
    "get_lead_api_leads__lead_id__get",
    "update_lead_status_api_leads__lead_id__status_patch",
    "get_runtime_settings_api_settings_get",
    "get_session_api_auth_session_get",
}

app = FastAPI(title=settings.app_name, lifespan=lifespan)

is_production_environment = settings.app_env.lower() in {"production", "prod"}
cors_allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"] if is_production_environment else ["*"]
cors_allow_headers = [
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-CSRF-Token",
    "X-Requested-With",
] if is_production_environment else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=cors_allow_methods,
    allow_headers=cors_allow_headers,
)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(profile_router)
app.include_router(leads_router)
app.include_router(settings_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "F1bot API is running."}


def _build_openapi() -> dict[str, Any]:
    """Return an OpenAPI schema with:
    - BearerAuth (HTTP Bearer / JWT) declared in securitySchemes.
    - All protected endpoints stamped with security: [{BearerAuth: []}].
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema: dict[str, Any] = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Inject security scheme.
    schema.setdefault("components", {})
    schema["components"].setdefault("securitySchemes", {})
    schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT access token obtained from /api/auth/login or /api/auth/register.",
    }

    # Stamp protected endpoints and strip any stale user_id query param.
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            if operation.get("operationId") in _PROTECTED_OPERATION_IDS:
                operation["security"] = [{"BearerAuth": []}]
                # Remove any legacy user_id query param that leaked from an old schema.
                operation["parameters"] = [
                    p for p in operation.get("parameters", [])
                    if not (p.get("in") == "query" and p.get("name") == "user_id")
                ]

    app.openapi_schema = schema
    return schema


app.openapi = _build_openapi  # type: ignore[method-assign]
