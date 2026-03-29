import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.api.dependencies import get_authenticated_user_id
from app.controllers.leads_controller import LeadsController
from app.core.constants import ERROR_LEAD_SCAN_FAILED
from app.core.scan_limits import enforce_scan_limits
from app.core.supabase_client import get_supabase_client
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


def _build_controller() -> LeadsController:
    repository = LeadsRepository(client=get_supabase_client())
    return LeadsController(repository=repository)


@router.post("/scan", response_model=LeadScanResponse)
async def scan_leads(
    payload: LeadScanRequest,
    current_user_id: str = Depends(get_authenticated_user_id),
) -> LeadScanResponse:
    enforce_scan_limits(current_user_id)
    controller = _build_controller()
    try:
        return await controller.scan(user_id=current_user_id, payload=payload)
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Lead scan failed for user %s: %s", current_user_id, error)
        raise HTTPException(status_code=500, detail=ERROR_LEAD_SCAN_FAILED) from error


@router.get("", response_model=LeadListResponse)
async def list_leads(
    status: LeadStatus | None = Query(default=None),
    current_user_id: str = Depends(get_authenticated_user_id),
) -> LeadListResponse:
    controller = _build_controller()
    return controller.list_leads(user_id=current_user_id, status=status)


@router.get("/export.csv", response_class=PlainTextResponse)
async def export_leads_csv(
    status: LeadStatus | None = Query(default=None),
    current_user_id: str = Depends(get_authenticated_user_id),
) -> PlainTextResponse:
    controller = _build_controller()
    csv_content = controller.export_csv(user_id=current_user_id, status=status)
    return PlainTextResponse(
        csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


@router.get("/{lead_id}", response_model=LeadRecord)
async def get_lead(lead_id: str, current_user_id: str = Depends(get_authenticated_user_id)) -> LeadRecord:
    controller = _build_controller()
    lead = controller.get_lead(user_id=current_user_id, lead_id=lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}/status", response_model=LeadRecord)
async def update_lead_status(
    lead_id: str,
    payload: LeadStatusUpdateRequest,
    current_user_id: str = Depends(get_authenticated_user_id),
) -> LeadRecord:
    controller = _build_controller()
    lead = controller.update_status(user_id=current_user_id, lead_id=lead_id, status=payload.status)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
