from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.models.schemas import LeadScanRequest, LeadScanResponse
from app.services.gemini_service import GeminiLeadScorer
from app.services.reddit_service import RedditLeadCollector

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.post("/scan", response_model=LeadScanResponse)
async def scan_leads(payload: LeadScanRequest) -> LeadScanResponse:
    settings = get_settings()

    collector = RedditLeadCollector(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent
    )
    scorer = GeminiLeadScorer(
        api_key=settings.gemini_api_key,
        model_lite=settings.gemini_model_lite,
        model_main=settings.gemini_model_main
    )

    try:
        candidate_posts = await collector.fetch_candidate_posts(payload)
        lead_insights = await scorer.score_posts(payload, candidate_posts)

        return LeadScanResponse(
            leads=lead_insights[: payload.limit],
            total_candidates=len(candidate_posts),
            used_ai=bool(settings.gemini_api_key)
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to scan leads: {error}") from error
