import csv
from io import StringIO
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

CSV_FORMULA_PREFIXES = ("=", "+", "-", "@")


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
        )

        # Load which Reddit posts this user has already seen so we skip them.
        seen_post_ids = self.repository.get_seen_post_ids(user_id)

        candidate_posts = await collector.fetch_candidate_posts(
            payload,
            seen_post_ids=seen_post_ids,
            allow_sample_fallback=settings.use_sample_leads_fallback(),
        )
        lead_insights = await scorer.score_posts(payload, candidate_posts)

        scan_id = str(uuid4())
        self.repository.save_scan_results(user_id, scan_id, lead_insights)

        # Mark every surfaced post as seen so next scan returns different leads.
        new_post_ids = {insight.post.id for insight in lead_insights}
        self.repository.mark_posts_seen(user_id, new_post_ids)

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
        output = StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(header)

        for lead in leads:
            writer.writerow(
                [
                    self._csv_safe_cell(lead.id),
                    self._csv_safe_cell(lead.status),
                    self._csv_safe_cell(lead.post.url),
                    self._csv_safe_cell(lead.post.subreddit),
                    self._csv_safe_cell(lead.lead_score),
                    self._csv_safe_cell(lead.qualification_reason),
                    self._csv_safe_cell(lead.suggested_outreach),
                ]
            )

        csv_output = output.getvalue()
        if csv_output.endswith("\n"):
            return csv_output[:-1]
        return csv_output

    def _csv_safe_cell(self, value: object) -> str:
        text = str(value)
        stripped = text.lstrip()
        if stripped and stripped[0] in CSV_FORMULA_PREFIXES:
            return f"'{text}"
        return text
