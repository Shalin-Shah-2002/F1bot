from __future__ import annotations

from contextlib import contextmanager
import importlib
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.constants import (
    ERROR_AUTH_LOCKED,
    ERROR_AUTH_RATE_LIMIT,
    ERROR_CSRF_TOKEN_INVALID,
    ERROR_LEAD_SCAN_FAILED,
    ERROR_SCAN_DAILY_QUOTA,
    ERROR_SCAN_RATE_LIMIT,
)


def _reset_runtime_state() -> None:
    from app.core.config import get_settings
    from app.core.scan_limits import reset_scan_limits_for_tests
    from app.core.supabase_client import get_supabase_admin_client, get_supabase_client

    get_settings.cache_clear()
    get_supabase_client.cache_clear()
    get_supabase_admin_client.cache_clear()
    reset_scan_limits_for_tests()


@contextmanager
def build_test_client(monkeypatch: pytest.MonkeyPatch, **env_overrides: str | None) -> Iterator[TestClient]:
    base_env: dict[str, str | None] = {
        "APP_ENV": "development",
        "SUPABASE_AUTH_ENABLED": "false",
        "LOCAL_AUTH_FALLBACK_ENABLED": "true",
        "SUPABASE_URL": "",
        "SUPABASE_ANON_KEY": "",
        "SUPABASE_SERVICE_ROLE_KEY": "",
        "RATE_LIMIT_STORE": "memory",
        "REDIS_URL": "",
        "REDIS_KEY_PREFIX": "f1bot:test:ratelimit",
        "SCAN_RATE_LIMIT_PER_MINUTE": "6",
        "SCAN_RATE_LIMIT_WINDOW_SECONDS": "60",
        "SCAN_DAILY_QUOTA": "200",
        "AUTH_RATE_LIMIT_PER_IP": "20",
        "AUTH_RATE_LIMIT_PER_IDENTITY": "8",
        "AUTH_RATE_LIMIT_WINDOW_SECONDS": "300",
        "AUTH_LOCKOUT_THRESHOLD": "5",
        "AUTH_LOCKOUT_BASE_SECONDS": "30",
        "AUTH_LOCKOUT_MAX_SECONDS": "900",
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


def test_scan_returns_seen_live_posts_instead_of_sample_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import datetime, timezone

    from app.models.schemas import CandidatePost, LeadInsight
    from app.repositories.leads_repository import LeadsRepository
    from app.services.gemini_service import GeminiLeadScorer
    from app.services.reddit_service import RedditLeadCollector

    live_post = CandidatePost(
        id="live-1",
        title="Need practical help with lead generation workflow",
        body="We keep hitting dead ends with tooling choices.",
        subreddit="entrepreneur",
        url="https://www.reddit.com/r/entrepreneur/comments/live1/test/",
        author="founder-live",
        created_utc=datetime.now(tz=timezone.utc),
        score=14,
        num_comments=5,
    )

    def _fake_seen_ids(self: LeadsRepository, user_id: str) -> set[str]:
        return {"live-1"}

    async def _fake_public_search(self: RedditLeadCollector, **_: object) -> list[CandidatePost]:
        return [live_post]

    def _fail_sample_fallback(self: RedditLeadCollector, request: object) -> list[CandidatePost]:
        raise AssertionError("Sample fallback should not run when live Reddit posts exist")

    async def _fake_score(
        self: GeminiLeadScorer,
        request: object,
        posts: list[CandidatePost],
    ) -> list[LeadInsight]:
        return [
            LeadInsight(
                post=post,
                lead_score=80,
                qualification_reason="Live post still relevant despite prior exposure.",
                suggested_outreach="Offer a concrete workflow audit.",
            )
            for post in posts
        ]

    monkeypatch.setattr(LeadsRepository, "get_seen_post_ids", _fake_seen_ids)
    monkeypatch.setattr(RedditLeadCollector, "_fetch_with_public_search", _fake_public_search)
    monkeypatch.setattr(RedditLeadCollector, "_sample_posts", _fail_sample_fallback)
    monkeypatch.setattr(GeminiLeadScorer, "score_posts", _fake_score)

    with build_test_client(monkeypatch, SAMPLE_LEADS_FALLBACK_ENABLED="true") as client:
        response = client.post("/api/leads/scan", json=SCAN_PAYLOAD, headers=AUTH_HEADERS)

    assert response.status_code == 200
    leads = response.json()["leads"]
    assert leads
    assert leads[0]["post"]["id"] == "live-1"
    assert not leads[0]["post"]["id"].startswith("sample-")


def test_scan_rate_limit_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services.gemini_service import GeminiLeadScorer
    from app.services.reddit_service import RedditLeadCollector

    async def _fake_fetch(
        self: RedditLeadCollector,
        request: object,
        seen_post_ids: set[str] | None = None,
        allow_sample_fallback: bool = True,
    ) -> list[object]:
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

    async def _fake_fetch(
        self: RedditLeadCollector,
        request: object,
        seen_post_ids: set[str] | None = None,
        allow_sample_fallback: bool = True,
    ) -> list[object]:
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


def test_startup_fails_if_local_fallback_not_opted_in(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(RuntimeError):
        with build_test_client(
            monkeypatch,
            APP_ENV="development",
            SUPABASE_AUTH_ENABLED="false",
            LOCAL_AUTH_FALLBACK_ENABLED="false",
            SUPABASE_URL=None,
            SUPABASE_SERVICE_ROLE_KEY=None,
        ):
            pass


def test_startup_runs_auth_limits_proxy_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.core.scan_limits as scan_limits_module

    def _raise_proxy_validation_error() -> None:
        raise RuntimeError("proxy startup validation triggered")

    monkeypatch.setattr(
        scan_limits_module,
        "validate_auth_limits_startup_configuration",
        _raise_proxy_validation_error,
    )

    with pytest.raises(RuntimeError, match="proxy startup validation triggered"):
        with build_test_client(monkeypatch):
            pass


def test_cors_uses_explicit_allowlists_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SUPABASE_AUTH_ENABLED", "false")
    monkeypatch.setenv("LOCAL_AUTH_FALLBACK_ENABLED", "true")

    _reset_runtime_state()

    import app.main as main_module

    importlib.reload(main_module)

    cors = next(m for m in main_module.app.user_middleware if m.cls.__name__ == "CORSMiddleware")

    assert cors.kwargs["allow_methods"] == ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    assert cors.kwargs["allow_headers"] == [
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-CSRF-Token",
        "X-Requested-With",
    ]
    assert "*" not in cors.kwargs["allow_methods"]
    assert "*" not in cors.kwargs["allow_headers"]

    _reset_runtime_state()


def test_settings_fail_closed_when_local_fallback_not_explicit() -> None:
    from app.core.config import Settings

    settings = Settings(
        _env_file=None,
        APP_ENV="development",
        LOCAL_AUTH_FALLBACK_ENABLED="false",
        SUPABASE_URL="",
        SUPABASE_SERVICE_ROLE_KEY="",
    )

    with pytest.raises(RuntimeError):
        settings.validate_auth_configuration()


def test_settings_parse_trusted_proxy_cidrs_from_csv() -> None:
    from app.core.config import Settings

    settings = Settings(
        _env_file=None,
        APP_ENV="development",
        SUPABASE_AUTH_ENABLED="false",
        LOCAL_AUTH_FALLBACK_ENABLED="true",
        TRUSTED_PROXY_CIDRS="10.0.0.0/8, 192.168.0.10",
    )

    assert settings.trusted_proxy_cidrs == ["10.0.0.0/8", "192.168.0.10"]


def test_settings_sample_leads_fallback_defaults_and_override() -> None:
    from app.core.config import Settings

    local_settings = Settings(
        _env_file=None,
        APP_ENV="development",
    )
    production_settings = Settings(
        _env_file=None,
        APP_ENV="production",
    )
    production_override = Settings(
        _env_file=None,
        APP_ENV="production",
        SAMPLE_LEADS_FALLBACK_ENABLED="true",
    )

    assert local_settings.use_sample_leads_fallback() is True
    assert production_settings.use_sample_leads_fallback() is False
    assert production_override.use_sample_leads_fallback() is True


def test_settings_require_redis_url_for_redis_rate_limit_store() -> None:
    from app.core.config import Settings

    settings = Settings(
        _env_file=None,
        APP_ENV="development",
        RATE_LIMIT_STORE="redis",
        REDIS_URL="",
    )

    with pytest.raises(RuntimeError):
        settings.validate_rate_limit_configuration()


def test_settings_disallow_memory_rate_limit_store_in_production() -> None:
    from app.core.config import Settings

    settings = Settings(
        _env_file=None,
        APP_ENV="production",
        RATE_LIMIT_STORE="memory",
    )

    with pytest.raises(RuntimeError):
        settings.validate_rate_limit_configuration()


def test_settings_require_anon_key_when_supabase_auth_enabled() -> None:
    from app.core.config import Settings

    settings = Settings(
        _env_file=None,
        APP_ENV="production",
        SUPABASE_AUTH_ENABLED="true",
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_ANON_KEY="",
    )

    with pytest.raises(RuntimeError):
        settings.validate_auth_configuration()


def test_settings_allow_supabase_auth_without_service_role_key() -> None:
    from app.core.config import Settings

    settings = Settings(
        _env_file=None,
        APP_ENV="production",
        SUPABASE_AUTH_ENABLED="true",
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_ANON_KEY="dummy-anon-key",
        SUPABASE_SERVICE_ROLE_KEY="",
    )

    settings.validate_auth_configuration()


def test_login_rate_limit_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi import HTTPException

    from app.controllers.auth_controller import AuthController

    def _reject_login(self: AuthController, payload: object) -> object:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    monkeypatch.setattr(AuthController, "login", _reject_login)

    payload = {"email": "rate-test@example.com", "password": "WrongPass123!"}

    with build_test_client(
        monkeypatch,
        AUTH_RATE_LIMIT_PER_IP="1",
        AUTH_RATE_LIMIT_PER_IDENTITY="1",
        AUTH_RATE_LIMIT_WINDOW_SECONDS="60",
        AUTH_LOCKOUT_THRESHOLD="10",
    ) as client:
        first = client.post("/api/auth/login", json=payload)
        second = client.post("/api/auth/login", json=payload)

    assert first.status_code == 401
    assert second.status_code == 429
    assert second.json() == {"detail": ERROR_AUTH_RATE_LIMIT}
    assert "retry-after" in {key.lower() for key in second.headers.keys()}


def test_login_lockout_enforced_after_repeated_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi import HTTPException

    from app.controllers.auth_controller import AuthController

    def _reject_login(self: AuthController, payload: object) -> object:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    monkeypatch.setattr(AuthController, "login", _reject_login)

    payload = {"email": "lockout-test@example.com", "password": "WrongPass123!"}

    with build_test_client(
        monkeypatch,
        AUTH_RATE_LIMIT_PER_IP="100",
        AUTH_RATE_LIMIT_PER_IDENTITY="100",
        AUTH_RATE_LIMIT_WINDOW_SECONDS="60",
        AUTH_LOCKOUT_THRESHOLD="2",
        AUTH_LOCKOUT_BASE_SECONDS="5",
        AUTH_LOCKOUT_MAX_SECONDS="5",
    ) as client:
        first = client.post("/api/auth/login", json=payload)
        second = client.post("/api/auth/login", json=payload)
        third = client.post("/api/auth/login", json=payload)

    assert first.status_code == 401
    assert second.status_code == 401
    assert third.status_code == 429
    assert third.json() == {"detail": ERROR_AUTH_LOCKED}
    assert "retry-after" in {key.lower() for key in third.headers.keys()}


def test_register_rate_limit_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi import HTTPException

    from app.controllers.auth_controller import AuthController

    def _reject_register(self: AuthController, payload: object) -> object:
        raise HTTPException(status_code=400, detail="Unable to create account")

    monkeypatch.setattr(AuthController, "register", _reject_register)

    payload = {
        "email": "register-rate-test@example.com",
        "password": "WrongPass123!",
        "full_name": "Rate Test",
    }

    with build_test_client(
        monkeypatch,
        AUTH_RATE_LIMIT_PER_IP="1",
        AUTH_RATE_LIMIT_PER_IDENTITY="1",
        AUTH_RATE_LIMIT_WINDOW_SECONDS="60",
        AUTH_LOCKOUT_THRESHOLD="10",
    ) as client:
        first = client.post("/api/auth/register", json=payload)
        second = client.post("/api/auth/register", json=payload)

    assert first.status_code == 400
    assert second.status_code == 429
    assert second.json() == {"detail": ERROR_AUTH_RATE_LIMIT}
    assert "retry-after" in {key.lower() for key in second.headers.keys()}


def test_login_sets_auth_and_csrf_cookies(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"email": "cookie-test@example.com", "password": "WrongPass123!"}

    with build_test_client(monkeypatch) as client:
        response = client.post("/api/auth/login", json=payload)
        session = client.get("/api/auth/session")

    assert response.status_code == 200
    set_cookie_headers = response.headers.get_list("set-cookie")

    access_cookie = next((value for value in set_cookie_headers if value.startswith("f1bot_access_token=")), "")
    csrf_cookie = next((value for value in set_cookie_headers if value.startswith("f1bot_csrf_token=")), "")

    assert access_cookie
    assert "httponly" in access_cookie.lower()
    assert "samesite=lax" in access_cookie.lower()
    assert csrf_cookie
    assert "httponly" not in csrf_cookie.lower()

    assert session.status_code == 200
    assert session.json()["email"] == payload["email"]


def test_cookie_auth_requires_csrf_for_mutations(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"email": "csrf-test@example.com", "password": "WrongPass123!"}
    profile_payload = {
        "business_description": "We help founders identify high intent Reddit conversations for outbound sales.",
        "keywords": ["founder", "outbound"],
        "subreddits": ["entrepreneur"],
    }

    with build_test_client(monkeypatch) as client:
        login_response = client.post("/api/auth/login", json=payload)
        missing_csrf = client.put("/api/profile", json=profile_payload)

        csrf_token = client.cookies.get("f1bot_csrf_token")
        with_csrf = client.put(
            "/api/profile",
            json=profile_payload,
            headers={"X-CSRF-Token": str(csrf_token or "")},
        )

    assert login_response.status_code == 200
    assert missing_csrf.status_code == 403
    assert missing_csrf.json() == {"detail": ERROR_CSRF_TOKEN_INVALID}
    assert with_csrf.status_code == 200


def test_logout_requires_csrf_when_cookie_session_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"email": "logout-csrf@example.com", "password": "WrongPass123!"}

    with build_test_client(monkeypatch) as client:
        login_response = client.post("/api/auth/login", json=payload)
        missing_csrf = client.post("/api/auth/logout")

        csrf_token = client.cookies.get("f1bot_csrf_token")
        with_csrf = client.post("/api/auth/logout", headers={"X-CSRF-Token": str(csrf_token or "")})
        session_after_logout = client.get("/api/auth/session")

    assert login_response.status_code == 200
    assert missing_csrf.status_code == 403
    assert missing_csrf.json() == {"detail": ERROR_CSRF_TOKEN_INVALID}
    assert with_csrf.status_code == 204
    assert session_after_logout.status_code == 401


def test_login_rejects_invalid_email_format(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"email": "not-an-email", "password": "WrongPass123!"}

    with build_test_client(monkeypatch) as client:
        response = client.post("/api/auth/login", json=payload)

    assert response.status_code == 422
    assert any(error["loc"][-1] == "email" for error in response.json()["detail"])


def test_login_rejects_weak_password(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"email": "weak-password@example.com", "password": "short123"}

    with build_test_client(monkeypatch) as client:
        response = client.post("/api/auth/login", json=payload)

    assert response.status_code == 422
    assert any(error["loc"][-1] == "password" for error in response.json()["detail"])


def test_register_rejects_weak_password(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "email": "weak-register@example.com",
        "password": "no-symbols123",
        "full_name": "Weak Register",
    }

    with build_test_client(monkeypatch) as client:
        response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 422
    assert any(error["loc"][-1] == "password" for error in response.json()["detail"])
