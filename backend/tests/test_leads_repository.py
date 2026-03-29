from __future__ import annotations

from datetime import datetime, timezone

from app.repositories.leads_repository import LeadsRepository


class _Result:
    def __init__(self, data: list[dict[str, object]]) -> None:
        self.data = data


class _SelectBuilder:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows
        self._filters: dict[str, object] = {}
        self._limit: int | None = None

    def eq(self, key: str, value: object) -> "_SelectBuilder":
        self._filters[key] = value
        return self

    def limit(self, value: int) -> "_SelectBuilder":
        self._limit = value
        return self

    def order(self, key: str, desc: bool = False) -> "_SelectBuilder":
        self._rows.sort(key=lambda item: item.get(key), reverse=desc)
        return self

    def execute(self) -> _Result:
        filtered = [
            row
            for row in self._rows
            if all(row.get(key) == value for key, value in self._filters.items())
        ]
        if self._limit is not None:
            filtered = filtered[: self._limit]
        return _Result(filtered)


class _UpdateBuilder:
    def __init__(self, rows: list[dict[str, object]], updates: dict[str, object]) -> None:
        self._rows = rows
        self._updates = updates
        self._filters: dict[str, object] = {}

    def eq(self, key: str, value: object) -> "_UpdateBuilder":
        self._filters[key] = value
        return self

    def execute(self) -> _Result:
        for row in self._rows:
            if all(row.get(key) == value for key, value in self._filters.items()):
                row.update(self._updates)
        return _Result([])


class _Table:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def select(self, _fields: str) -> _SelectBuilder:
        return _SelectBuilder(self._rows)

    def update(self, updates: dict[str, object]) -> _UpdateBuilder:
        return _UpdateBuilder(self._rows, updates)


class _FakeSupabaseClient:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._table = _Table(rows)

    def table(self, name: str) -> _Table:
        assert name == "leads"
        return self._table


def _lead_row() -> dict[str, object]:
    now = datetime.now(tz=timezone.utc).isoformat()
    return {
        "id": "lead-1",
        "user_id": "user-1",
        "status": "new",
        "post_id": "post-1",
        "title": "Post title",
        "body": "Post body",
        "subreddit": "entrepreneur",
        "url": "https://reddit.com/r/entrepreneur/post-1",
        "author": "author-1",
        "post_created_utc": now,
        "reddit_score": 10,
        "num_comments": 2,
        "lead_score": 87.5,
        "qualification_reason": "Good fit",
        "suggested_outreach": "Helpful outreach",
        "scan_id": "scan-1",
        "created_at": now,
        "updated_at": now,
    }


def test_update_status_works_without_update_select_chain_support() -> None:
    row = _lead_row()
    client = _FakeSupabaseClient([row])
    repository = LeadsRepository(client=client)

    updated = repository.update_status(user_id="user-1", lead_id="lead-1", status="contacted")

    assert updated is not None
    assert updated.status == "contacted"
    assert row["status"] == "contacted"
