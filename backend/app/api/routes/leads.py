import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.api.dependencies import AuthContext, get_authenticated_context, require_csrf_for_cookie_auth
from app.core.config import get_settings
from app.controllers.leads_controller import LeadsController
from app.core.constants import ERROR_AUTH_CONFIGURATION, ERROR_LEAD_SCAN_FAILED
from app.core.scan_limits import enforce_scan_limits
from app.core.supabase_client import get_supabase_user_client
from app.models.schemas import (
    LeadListResponse,
    LeadRecord,
    LeadScanRequest,
    LeadScanResponse,
    LeadStatus,
    LeadStatusUpdateRequest,
)
from app.repositories.leads_repository import LeadsRepository

router = APIRouter(prefix="/api/leads", tags=["leads"])
logger = logging.getLogger(__name__)


def _build_controller(auth_context: AuthContext) -> LeadsController:
    """Build a LeadsController wired to the right storage backend.

    When Supabase auth is disabled (local / demo mode), ``get_supabase_user_client``
    returns ``None`` and the repository falls back to the in-memory store.
    When Supabase auth is enabled the client carries the user JWT for RLS and
    we raise 500 if it could not be created.
    """
    settings = get_settings()
    client = get_supabase_user_client(auth_context.access_token)
    if settings.use_supabase_auth() and client is None:
        raise HTTPException(status_code=500, detail=ERROR_AUTH_CONFIGURATION)

    repository = LeadsRepository(client=client)
    return LeadsController(repository=repository)


@router.post("/scan", response_model=LeadScanResponse, dependencies=[Depends(require_csrf_for_cookie_auth)])
async def scan_leads(
    payload: LeadScanRequest,
    auth_context: AuthContext = Depends(get_authenticated_context),
) -> LeadScanResponse:
    enforce_scan_limits(auth_context.user_id)
    controller = _build_controller(auth_context)
    try:
        return await controller.scan(user_id=auth_context.user_id, payload=payload)
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Lead scan failed for user %s: %s", auth_context.user_id, error)
        raise HTTPException(status_code=500, detail=ERROR_LEAD_SCAN_FAILED) from error


@router.get("", response_model=LeadListResponse)
async def list_leads(
    status: LeadStatus | None = Query(default=None),
    auth_context: AuthContext = Depends(get_authenticated_context),
) -> LeadListResponse:
    controller = _build_controller(auth_context)
    return controller.list_leads(user_id=auth_context.user_id, status=status)


@router.get("/export.csv", response_class=PlainTextResponse)
async def export_leads_csv(
    status: LeadStatus | None = Query(default=None),
    auth_context: AuthContext = Depends(get_authenticated_context),
) -> PlainTextResponse:
    controller = _build_controller(auth_context)
    csv_content = controller.export_csv(user_id=auth_context.user_id, status=status)
    return PlainTextResponse(
        csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


@router.get("/{lead_id}", response_model=LeadRecord)
async def get_lead(
    lead_id: str,
    auth_context: AuthContext = Depends(get_authenticated_context),
) -> LeadRecord:
    controller = _build_controller(auth_context)
    lead = controller.get_lead(user_id=auth_context.user_id, lead_id=lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}/status", response_model=LeadRecord, dependencies=[Depends(require_csrf_for_cookie_auth)])
async def update_lead_status(
    lead_id: str,
    payload: LeadStatusUpdateRequest,
    auth_context: AuthContext = Depends(get_authenticated_context),
) -> LeadRecord:
    controller = _build_controller(auth_context)
    lead = controller.update_status(user_id=auth_context.user_id, lead_id=lead_id, status=payload.status)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
