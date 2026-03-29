from __future__ import annotations

from contextlib import contextmanager
import importlib
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.constants import (
    ERROR_LEAD_SCAN_FAILED,
    ERROR_SCAN_DAILY_QUOTA,
    ERROR_SCAN_RATE_LIMIT,
)


def _reset_runtime_state() -> None:
    from app.core.config import get_settings
    from app.core.scan_limits import reset_scan_limits_for_tests
    from app.core.supabase_client import get_supabase_client

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    reset_scan_limits_for_tests()


@contextmanager
def build_test_client(monkeypatch: pytest.MonkeyPatch, **env_overrides: str | None) -> Iterator[TestClient]:
    base_env: dict[str, str | None] = {
        "APP_ENV": "development",
        "SUPABASE_AUTH_ENABLED": "false",
        "SUPABASE_URL": None,
        "SUPABASE_SERVICE_ROLE_KEY": None,
        "SCAN_RATE_LIMIT_PER_MINUTE": "6",
        "SCAN_RATE_LIMIT_WINDOW_SECONDS": "60",
        "SCAN_DAILY_QUOTA": "200",
    }
    base_env.update(env_overrides)

    for key, value in base_env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)

    _reset_runtime_state()

    import app.main as main_module

    importlib.reload(main_module)

    with TestClient(main_module.app) as client:
        yield client

    _reset_runtime_state()


AUTH_HEADERS = {"Authorization": "Bearer demo-token-test-user"}
SCAN_PAYLOAD = {
    "business_description": "We help B2B SaaS founders improve conversion from website traffic to demos.",
    "keywords": ["conversion", "landing page"],
    "subreddits": ["entrepreneur"],
    "limit": 2,
}


def test_health_requires_authorization_header(monkeypatch: pytest.MonkeyPatch) -> None:
    with build_test_client(monkeypatch) as client:
        response = client.get("/api/health")

    assert response.status_code == 401


def test_health_accepts_local_demo_token(monkeypatch: pytest.MonkeyPatch) -> None:
    with build_test_client(monkeypatch) as client:
        response = client.get("/api/health", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scan_error_response_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.controllers.leads_controller import LeadsController

    async def _raise_error(self: LeadsController, user_id: str, payload: dict[str, object]) -> object:
        raise RuntimeError("sensitive internal details")

    monkeypatch.setattr(LeadsController, "scan", _raise_error)

    with build_test_client(monkeypatch) as client:
        response = client.post("/api/leads/scan", json=SCAN_PAYLOAD, headers=AUTH_HEADERS)

    assert response.status_code == 500
    assert response.json() == {"detail": ERROR_LEAD_SCAN_FAILED}
    assert "sensitive" not in response.text


def test_scan_rate_limit_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services.gemini_service import GeminiLeadScorer
    from app.services.reddit_service import RedditLeadCollector

    async def _fake_fetch(self: RedditLeadCollector, request: object) -> list[object]:
        return []

    async def _fake_score(self: GeminiLeadScorer, request: object, posts: list[object]) -> list[object]:
        return []

    monkeypatch.setattr(RedditLeadCollector, "fetch_candidate_posts", _fake_fetch)
    monkeypatch.setattr(GeminiLeadScorer, "score_posts", _fake_score)

    with build_test_client(
        monkeypatch,
        SCAN_RATE_LIMIT_PER_MINUTE="1",
        SCAN_RATE_LIMIT_WINDOW_SECONDS="60",
        SCAN_DAILY_QUOTA="10",
    ) as client:
        first = client.post("/api/leads/scan", json=SCAN_PAYLOAD, headers=AUTH_HEADERS)
        second = client.post("/api/leads/scan", json=SCAN_PAYLOAD, headers=AUTH_HEADERS)

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json() == {"detail": ERROR_SCAN_RATE_LIMIT}
    assert "retry-after" in {key.lower() for key in second.headers.keys()}


def test_scan_daily_quota_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services.gemini_service import GeminiLeadScorer
    from app.services.reddit_service import RedditLeadCollector

    async def _fake_fetch(self: RedditLeadCollector, request: object) -> list[object]:
        return []

    async def _fake_score(self: GeminiLeadScorer, request: object, posts: list[object]) -> list[object]:
        return []

    monkeypatch.setattr(RedditLeadCollector, "fetch_candidate_posts", _fake_fetch)
    monkeypatch.setattr(GeminiLeadScorer, "score_posts", _fake_score)

    with build_test_client(
        monkeypatch,
        SCAN_RATE_LIMIT_PER_MINUTE="10",
        SCAN_RATE_LIMIT_WINDOW_SECONDS="60",
        SCAN_DAILY_QUOTA="1",
    ) as client:
        first = client.post("/api/leads/scan", json=SCAN_PAYLOAD, headers=AUTH_HEADERS)
        second = client.post("/api/leads/scan", json=SCAN_PAYLOAD, headers=AUTH_HEADERS)

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json() == {"detail": ERROR_SCAN_DAILY_QUOTA}


def test_startup_fails_if_auth_disabled_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(RuntimeError):
        with build_test_client(
            monkeypatch,
            APP_ENV="production",
            SUPABASE_AUTH_ENABLED="false",
            SUPABASE_URL=None,
            SUPABASE_SERVICE_ROLE_KEY=None,
        ):
            pass
