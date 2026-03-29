from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.models.schemas import CandidatePost, LeadInsight, LeadRecord, LeadStatus
from app.repositories.memory_store import MEMORY_LEADS

SupabaseClient = Any


class LeadsRepository:
    def __init__(self, client: SupabaseClient | None) -> None:
        self.client = client

    def save_scan_results(self, user_id: str, scan_id: str, insights: list[LeadInsight]) -> list[LeadRecord]:
        now = datetime.now(tz=timezone.utc)
        records: list[LeadRecord] = []

        for insight in insights:
            record = LeadRecord(
                id=str(uuid4()),
                user_id=user_id,
                status="new",
                post=insight.post,
                lead_score=insight.lead_score,
                qualification_reason=insight.qualification_reason,
                suggested_outreach=insight.suggested_outreach,
                scan_id=scan_id,
                created_at=now,
                updated_at=now
            )
            records.append(record)

        if not records:
            return []

        if self.client is None:
            for record in records:
                MEMORY_LEADS[record.id] = record
            return records

        payload = [self._to_row(item) for item in records]
        self.client.table("leads").insert(payload).execute()
        return records

    def list_leads(self, user_id: str, status: LeadStatus | None = None) -> list[LeadRecord]:
        if self.client is None:
            items = [lead for lead in MEMORY_LEADS.values() if lead.user_id == user_id]
            if status:
                items = [lead for lead in items if lead.status == status]
            return sorted(items, key=lambda row: row.lead_score, reverse=True)

        query = self.client.table("leads").select("*").eq("user_id", user_id)
        if status:
            query = query.eq("status", status)

        rows = query.order("lead_score", desc=True).execute().data or []
        return [self._from_row(row) for row in rows]

    def get_lead(self, user_id: str, lead_id: str) -> LeadRecord | None:
        if self.client is None:
            lead = MEMORY_LEADS.get(lead_id)
            if not lead or lead.user_id != user_id:
                return None
            return lead

        rows = (
            self.client.table("leads")
            .select("*")
            .eq("id", lead_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
            .data
            or []
        )

        if not rows:
            return None

        return self._from_row(rows[0])

    def update_status(self, user_id: str, lead_id: str, status: LeadStatus) -> LeadRecord | None:
        now = datetime.now(tz=timezone.utc)

        if self.client is None:
            lead = MEMORY_LEADS.get(lead_id)
            if not lead or lead.user_id != user_id:
                return None
            updated = lead.model_copy(update={"status": status, "updated_at": now})
            MEMORY_LEADS[lead_id] = updated
            return updated

        # Keep update and fetch separate for supabase-py compatibility across versions.
        self.client.table("leads").update(
            {"status": status, "updated_at": now.isoformat()}
        ).eq("id", lead_id).eq("user_id", user_id).execute()

        return self.get_lead(user_id=user_id, lead_id=lead_id)

    def _to_row(self, record: LeadRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "user_id": record.user_id,
            "status": record.status,
            "post_id": record.post.id,
            "title": record.post.title,
            "body": record.post.body,
            "subreddit": record.post.subreddit,
            "url": record.post.url,
            "author": record.post.author,
            "post_created_utc": record.post.created_utc.isoformat(),
            "reddit_score": record.post.score,
            "num_comments": record.post.num_comments,
            "lead_score": record.lead_score,
            "qualification_reason": record.qualification_reason,
            "suggested_outreach": record.suggested_outreach,
            "scan_id": record.scan_id,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat()
        }

    def _from_row(self, row: dict[str, object]) -> LeadRecord:
        post = CandidatePost(
            id=str(row.get("post_id", "")),
            title=str(row.get("title", "")),
            body=str(row.get("body", "")),
            subreddit=str(row.get("subreddit", "")),
            url=str(row.get("url", "")),
            author=str(row.get("author", "unknown")),
            created_utc=self._parse_datetime(row.get("post_created_utc")),
            score=int(row.get("reddit_score", 0) or 0),
            num_comments=int(row.get("num_comments", 0) or 0)
        )

        return LeadRecord(
            id=str(row.get("id", "")),
            user_id=str(row.get("user_id", "")),
            status=str(row.get("status", "new")),
            post=post,
            lead_score=float(row.get("lead_score", 0) or 0),
            qualification_reason=str(row.get("qualification_reason", "")),
            suggested_outreach=str(row.get("suggested_outreach", "")),
            scan_id=str(row.get("scan_id", "")),
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at"))
        )

    def _parse_datetime(self, value: object) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value:
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.now(tz=timezone.utc)
