"""
Tests for client IP resolution and rate-limit bucket isolation.

Acceptance Criteria:
  AC1. Requests behind trusted proxies rate-limited per true client IP (X-Forwarded-For).
  AC2. Requests from non-trusted peers use request.client.host only (XFF ignored).
  AC3. TRUSTED_PROXY_CIDRS is the configuration surface.

Coverage beyond existing test_client_ip.py unit tests:
  - resolve_client_ip(request) when request.client is None  → "unknown"
  - Spoofed X-Forwarded-For from untrusted peer → ignored, peer IP wins
  - Single trusted proxy hop → leftmost XFF IP used
  - Double trusted proxy hop → correct client IP extracted
  - All-trusted XFF chain (internal only) → falls back to peer IP
  - "unknown" bucket: rate-limit counter still advances (no crash)
  - Two different real IPs behind a trusted proxy → separate buckets
  - Same real IP behind a trusted proxy → shared bucket
"""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.core.client_ip import (
    UNKNOWN_REMOTE_IP,
    _resolve_client_ip,
    resolve_client_ip,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(
    peer_host: str | None,
    x_forwarded_for: str | None = None,
) -> MagicMock:
    """Build a minimal mock that looks like a Starlette Request."""
    request = MagicMock()
    if peer_host is None:
        request.client = None
    else:
        request.client = MagicMock()
        request.client.host = peer_host

    headers: dict[str, str] = {}
    if x_forwarded_for is not None:
        headers["x-forwarded-for"] = x_forwarded_for
    request.headers = headers
    return request


# ---------------------------------------------------------------------------
# resolve_client_ip – integration over the real Request object shape
# ---------------------------------------------------------------------------

class TestResolveClientIpWithRequest:
    """Tests that exercise resolve_client_ip() with a mocked Request and
    monkeypatched settings, covering the full call path used in production."""

    def test_none_client_returns_unknown(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AC: request.client is None → 'unknown', no crash."""
        from app.core import client_ip as module

        monkeypatch.setattr(
            module, "get_settings",
            lambda: MagicMock(trusted_proxy_cidrs=[]),
        )

        request = _make_request(peer_host=None, x_forwarded_for="1.2.3.4")
        assert resolve_client_ip(request) == UNKNOWN_REMOTE_IP

    def test_no_trusted_proxies_uses_peer_ip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AC2: no trusted proxies → peer IP always wins, XFF ignored."""
        from app.core import client_ip as module

        monkeypatch.setattr(
            module, "get_settings",
            lambda: MagicMock(trusted_proxy_cidrs=[]),
        )

        request = _make_request(
            peer_host="203.0.113.99",
            x_forwarded_for="198.51.100.1",  # attacker-supplied
        )
        # XFF must be ignored when no trusted proxies configured.
        assert resolve_client_ip(request) == "203.0.113.99"

    def test_spoofed_xff_from_untrusted_peer_is_ignored(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AC2: attacker sends X-Forwarded-For from an untrusted connection.
        The peer IP (attacker's real IP) must be returned, not the forged header."""
        from app.core import client_ip as module

        monkeypatch.setattr(
            module, "get_settings",
            lambda: MagicMock(trusted_proxy_cidrs=["10.0.0.0/8"]),
        )

        # Attacker's IP is NOT in the trusted CIDR, so XFF must be ignored.
        request = _make_request(
            peer_host="203.0.113.55",             # attacker
            x_forwarded_for="198.51.100.1",       # spoofed victim IP
        )
        assert resolve_client_ip(request) == "203.0.113.55"

    def test_single_trusted_proxy_hop_extracts_real_client_ip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AC1: one trusted proxy hop → leftmost XFF entry is the real client IP."""
        from app.core import client_ip as module

        monkeypatch.setattr(
            module, "get_settings",
            lambda: MagicMock(trusted_proxy_cidrs=["10.0.0.0/8"]),
        )

        # Request arrives from trusted LB at 10.0.0.1; real client is 198.51.100.25.
        request = _make_request(
            peer_host="10.0.0.1",
            x_forwarded_for="198.51.100.25",
        )
        assert resolve_client_ip(request) == "198.51.100.25"

    def test_double_trusted_proxy_hop_extracts_nearest_untrusted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AC1: two trusted proxy hops → innermost untrusted hop wins."""
        from app.core import client_ip as module

        monkeypatch.setattr(
            module, "get_settings",
            lambda: MagicMock(trusted_proxy_cidrs=["10.0.0.0/8"]),
        )

        # Chain: real_client → proxy1(10.0.0.1) → proxy2(10.0.0.2) → app
        request = _make_request(
            peer_host="10.0.0.2",
            x_forwarded_for="198.51.100.25, 10.0.0.1",
        )
        assert resolve_client_ip(request) == "198.51.100.25"

    def test_all_trusted_chain_falls_back_to_peer_ip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Edge case: every hop in XFF is trusted → fall back to the innermost peer."""
        from app.core import client_ip as module

        monkeypatch.setattr(
            module, "get_settings",
            lambda: MagicMock(trusted_proxy_cidrs=["10.0.0.0/8"]),
        )

        # All IPs in the chain (including peer) are internal/trusted.
        request = _make_request(
            peer_host="10.0.0.3",
            x_forwarded_for="10.0.0.1, 10.0.0.2",
        )
        # _resolve_client_ip returns peer_ip when all hops are trusted.
        assert resolve_client_ip(request) == "10.0.0.3"


# ---------------------------------------------------------------------------
# _resolve_client_ip – pure unit tests for edge-case tokens
# ---------------------------------------------------------------------------

class TestResolveClientIpPure:
    """Pure-function tests that do not need monkeypatched settings."""

    def test_ipv6_peer_no_trusted_proxies(self) -> None:
        resolved = _resolve_client_ip(
            peer_ip="2001:db8::1",
            x_forwarded_for=None,
            trusted_proxy_cidrs=[],
        )
        assert resolved == "2001:db8::1"

    def test_xff_with_port_notation_stripped(self) -> None:
        """Some proxies include port (e.g. '1.2.3.4:12345') – must still resolve."""
        resolved = _resolve_client_ip(
            peer_ip="10.0.0.1",
            x_forwarded_for="203.0.113.7:54321",
            trusted_proxy_cidrs=["10.0.0.0/8"],
        )
        assert resolved == "203.0.113.7"

    def test_xff_with_rfc7239_for_prefix(self) -> None:
        """RFC 7239 Forwarded header style: 'for=203.0.113.7'."""
        resolved = _resolve_client_ip(
            peer_ip="10.0.0.1",
            x_forwarded_for="for=203.0.113.7",
            trusted_proxy_cidrs=["10.0.0.0/8"],
        )
        assert resolved == "203.0.113.7"

    def test_malformed_xff_tokens_are_skipped(self) -> None:
        """Garbage tokens in XFF should not crash; valid ones still used."""
        resolved = _resolve_client_ip(
            peer_ip="10.0.0.1",
            x_forwarded_for="not-an-ip, 203.0.113.99",
            trusted_proxy_cidrs=["10.0.0.0/8"],
        )
        assert resolved == "203.0.113.99"

    def test_empty_xff_header_uses_peer_ip(self) -> None:
        resolved = _resolve_client_ip(
            peer_ip="203.0.113.10",
            x_forwarded_for="",
            trusted_proxy_cidrs=["10.0.0.0/8"],
        )
        assert resolved == "203.0.113.10"

    def test_whitespace_only_xff_uses_peer_ip(self) -> None:
        resolved = _resolve_client_ip(
            peer_ip="203.0.113.10",
            x_forwarded_for="   ",
            trusted_proxy_cidrs=["10.0.0.0/8"],
        )
        assert resolved == "203.0.113.10"


# ---------------------------------------------------------------------------
# Rate-limit bucket isolation
# ---------------------------------------------------------------------------

class TestRateLimitBucketIsolation:
    """Verifies that the IP buckets used by the rate limiter are correctly
    isolated when IPs differ and shared when IPs are the same."""

    def test_unknown_ip_bucket_does_not_crash_rate_limiter(self) -> None:
        """'unknown' as remote_ip must not raise; the bucket advances normally."""
        from app.core.scan_limits import InMemoryRateLimitStore
        from app.core.config import Settings

        settings = Settings(
            _env_file=None,
            APP_ENV="development",
            SUPABASE_AUTH_ENABLED="false",
            LOCAL_AUTH_FALLBACK_ENABLED="true",
            RATE_LIMIT_STORE="memory",
            AUTH_RATE_LIMIT_PER_IP="10",
            AUTH_RATE_LIMIT_PER_IDENTITY="10",
            AUTH_RATE_LIMIT_WINDOW_SECONDS="60",
            AUTH_LOCKOUT_THRESHOLD="5",
            AUTH_LOCKOUT_BASE_SECONDS="30",
            AUTH_LOCKOUT_MAX_SECONDS="900",
        )
        store = InMemoryRateLimitStore()
        # Should not raise even with the sentinel "unknown" IP.
        store.enforce_auth_limits(UNKNOWN_REMOTE_IP, "user@example.com", settings)

    def test_different_real_ips_use_separate_buckets(self) -> None:
        """AC1: two clients with distinct real IPs (resolved through a proxy) must
        consume from separate rate-limit buckets."""
        from app.core.scan_limits import InMemoryRateLimitStore
        from app.core.config import Settings

        settings = Settings(
            _env_file=None,
            APP_ENV="development",
            SUPABASE_AUTH_ENABLED="false",
            LOCAL_AUTH_FALLBACK_ENABLED="true",
            RATE_LIMIT_STORE="memory",
            AUTH_RATE_LIMIT_PER_IP="1",  # tight limit to expose bucket sharing bugs
            AUTH_RATE_LIMIT_PER_IDENTITY="100",
            AUTH_RATE_LIMIT_WINDOW_SECONDS="60",
            AUTH_LOCKOUT_THRESHOLD="50",
            AUTH_LOCKOUT_BASE_SECONDS="30",
            AUTH_LOCKOUT_MAX_SECONDS="900",
        )
        store = InMemoryRateLimitStore()

        ip_a = "198.51.100.1"  # client A behind trusted proxy
        ip_b = "198.51.100.2"  # client B behind trusted proxy

        # First request from each IP must be allowed independently.
        store.enforce_auth_limits(ip_a, "a@example.com", settings)   # uses ip_a's bucket
        store.enforce_auth_limits(ip_b, "b@example.com", settings)   # uses ip_b's separate bucket

    def test_same_real_ip_shares_single_bucket(self) -> None:
        """The second request from the same (resolved) IP must be rejected
        once the per-IP limit is hit, proving they share one bucket."""
        from fastapi import HTTPException
        from app.core.scan_limits import InMemoryRateLimitStore
        from app.core.config import Settings

        settings = Settings(
            _env_file=None,
            APP_ENV="development",
            SUPABASE_AUTH_ENABLED="false",
            LOCAL_AUTH_FALLBACK_ENABLED="true",
            RATE_LIMIT_STORE="memory",
            AUTH_RATE_LIMIT_PER_IP="1",
            AUTH_RATE_LIMIT_PER_IDENTITY="100",
            AUTH_RATE_LIMIT_WINDOW_SECONDS="60",
            AUTH_LOCKOUT_THRESHOLD="50",
            AUTH_LOCKOUT_BASE_SECONDS="30",
            AUTH_LOCKOUT_MAX_SECONDS="900",
        )
        store = InMemoryRateLimitStore()

        resolved_ip = "198.51.100.10"

        # First request: allowed.
        store.enforce_auth_limits(resolved_ip, "user@example.com", settings)

        # Second request from the same resolved IP: must be blocked.
        with pytest.raises(HTTPException) as exc_info:
            store.enforce_auth_limits(resolved_ip, "user@example.com", settings)

        assert exc_info.value.status_code == 429
