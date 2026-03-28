from uuid import uuid4

from app.core.config import get_settings
from app.models.schemas import (
    LeadInsight,
    LeadListResponse,
    LeadRecord,
    LeadScanRequest,
    LeadScanResponse,
    LeadStatus,
)
from app.repositories.leads_repository import LeadsRepository
from app.services.gemini_service import GeminiLeadScorer
from app.services.reddit_service import RedditLeadCollector


class LeadsController:
    def __init__(self, repository: LeadsRepository) -> None:
        self.repository = repository

    async def scan(self, user_id: str, payload: LeadScanRequest) -> LeadScanResponse:
        settings = get_settings()

        collector = RedditLeadCollector(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )
        scorer = GeminiLeadScorer(
            api_key=settings.gemini_api_key,
            model_lite=settings.gemini_model_lite,
            model_main=settings.gemini_model_main,
        )

        candidate_posts = await collector.fetch_candidate_posts(payload)
        lead_insights = await scorer.score_posts(payload, candidate_posts)

        scan_id = str(uuid4())
        self.repository.save_scan_results(user_id, scan_id, lead_insights)

        return LeadScanResponse(
            leads=lead_insights[: payload.limit],
            total_candidates=len(candidate_posts),
            used_ai=bool(settings.gemini_api_key),
        )

    def list_leads(self, user_id: str, status: LeadStatus | None = None) -> LeadListResponse:
        leads = self.repository.list_leads(user_id=user_id, status=status)
        return LeadListResponse(leads=leads)

    def get_lead(self, user_id: str, lead_id: str) -> LeadRecord | None:
        return self.repository.get_lead(user_id=user_id, lead_id=lead_id)

    def update_status(self, user_id: str, lead_id: str, status: LeadStatus) -> LeadRecord | None:
        return self.repository.update_status(user_id=user_id, lead_id=lead_id, status=status)

    def export_csv(self, user_id: str, status: LeadStatus | None = None) -> str:
        leads = self.repository.list_leads(user_id=user_id, status=status)

        header = [
            "lead_id",
            "status",
            "post_url",
            "subreddit",
            "lead_score",
            "qualification_reason",
            "suggested_outreach",
        ]
        rows = [",".join(header)]

        for lead in leads:
            values = [
                lead.id,
                lead.status,
                lead.post.url,
                lead.post.subreddit,
                str(lead.lead_score),
                self._csv_escape(lead.qualification_reason),
                self._csv_escape(lead.suggested_outreach),
            ]
            rows.append(",".join(values))

        return "\n".join(rows)

    def _csv_escape(self, value: str) -> str:
        escaped = value.replace('"', '""')
        return f'"{escaped}"'
