from __future__ import annotations

from contextlib import contextmanager
import importlib
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.constants import (
    ERROR_AUTH_LOCKED,
    ERROR_AUTH_RATE_LIMIT,
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


def test_scan_rate_limit_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services.gemini_service import GeminiLeadScorer
    from app.services.reddit_service import RedditLeadCollector

    async def _fake_fetch(
        self: RedditLeadCollector,
        request: object,
        seen_post_ids: set[str] | None = None,
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

    payload = {"email": "rate-test@example.com", "password": "wrong-password"}

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

    payload = {"email": "lockout-test@example.com", "password": "wrong-password"}

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
        "password": "wrong-password",
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
