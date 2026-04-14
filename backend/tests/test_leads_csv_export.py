from __future__ import annotations

import csv
from datetime import datetime, timezone
from io import StringIO

from app.controllers.leads_controller import LeadsController
from app.models.schemas import CandidatePost, LeadRecord


class _FakeLeadsRepository:
    def __init__(self, leads: list[LeadRecord]) -> None:
        self._leads = leads

    def list_leads(self, user_id: str, status: str | None = None) -> list[LeadRecord]:
        if status is None:
            return self._leads
        return [lead for lead in self._leads if lead.status == status]


def _build_lead(
    *,
    lead_id: str,
    post_url: str,
    subreddit: str,
    qualification_reason: str,
    suggested_outreach: str,
) -> LeadRecord:
    now = datetime.now(tz=timezone.utc)
    return LeadRecord(
        id=lead_id,
        user_id="user-1",
        status="new",
        post=CandidatePost(
            id="post-1",
            title="Help needed",
            body="Body",
            subreddit=subreddit,
            url=post_url,
            author="author",
            created_utc=now,
            score=10,
            num_comments=3,
        ),
        lead_score=92.5,
        qualification_reason=qualification_reason,
        suggested_outreach=suggested_outreach,
        scan_id="scan-1",
        created_at=now,
        updated_at=now,
    )


def test_export_csv_neutralizes_formula_leading_characters() -> None:
    lead = _build_lead(
        lead_id="=lead-1",
        post_url="+https://example.com/post",
        subreddit="-growth",
        qualification_reason='=@SUM("A1:A2")',
        suggested_outreach="   @malicious",
    )

    controller = LeadsController(repository=_FakeLeadsRepository([lead]))
    csv_text = controller.export_csv(user_id="user-1")
    rows = list(csv.reader(StringIO(csv_text)))

    assert rows[0] == [
        "lead_id",
        "status",
        "post_url",
        "subreddit",
        "lead_score",
        "qualification_reason",
        "suggested_outreach",
    ]
    assert rows[1][0] == "'=lead-1"
    assert rows[1][2] == "'+https://example.com/post"
    assert rows[1][3] == "'-growth"
    assert rows[1][5] == "'=@SUM(\"A1:A2\")"
    assert rows[1][6] == "'   @malicious"


def test_export_csv_preserves_non_formula_cells() -> None:
    lead = _build_lead(
        lead_id="lead-2",
        post_url="https://example.com/post-2",
        subreddit="entrepreneur",
        qualification_reason='Contains "quotes" safely',
        suggested_outreach="Reach out with helpful case study",
    )

    controller = LeadsController(repository=_FakeLeadsRepository([lead]))
    csv_text = controller.export_csv(user_id="user-1")
    row = list(csv.reader(StringIO(csv_text)))[1]

    assert row[0] == "lead-2"
    assert row[2] == "https://example.com/post-2"
    assert row[3] == "entrepreneur"
    assert row[5] == 'Contains "quotes" safely'
    assert row[6] == "Reach out with helpful case study"
