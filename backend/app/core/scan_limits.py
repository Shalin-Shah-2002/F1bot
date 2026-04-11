from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib
import logging
from threading import Lock
import time

from fastapi import HTTPException

from app.core.config import get_settings
from app.core.constants import (
    ERROR_AUTH_LOCKED,
    ERROR_AUTH_RATE_LIMIT,
    ERROR_SCAN_DAILY_QUOTA,
    ERROR_SCAN_RATE_LIMIT,
)

logger = logging.getLogger(__name__)


_SCAN_RATE_WINDOWS: dict[str, deque[float]] = defaultdict(deque)
_SCAN_DAILY_USAGE: dict[str, tuple[str, int]] = {}

_AUTH_RATE_WINDOWS_BY_IP: dict[str, deque[float]] = defaultdict(deque)
_AUTH_RATE_WINDOWS_BY_IDENTITY: dict[str, deque[float]] = defaultdict(deque)
_AUTH_FAILURE_STREAK: dict[str, int] = defaultdict(int)
_AUTH_LOCKED_UNTIL: dict[str, float] = {}

_LOCK = Lock()


def _current_utc_day() -> str:
    return datetime.now(tz=timezone.utc).date().isoformat()


def _prune_window(window: deque[float], cutoff: float) -> None:
    while window and window[0] <= cutoff:
        window.popleft()


def _normalize_identity(identity: str | None) -> str:
    return (identity or "").strip().lower()


def _fingerprint(identity: str) -> str:
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]


def enforce_scan_limits(user_id: str) -> None:
    settings = get_settings()
    now_ts = time.time()
    today = _current_utc_day()

    with _LOCK:
        usage_day, usage_count = _SCAN_DAILY_USAGE.get(user_id, (today, 0))
        if usage_day != today:
            usage_day, usage_count = today, 0

        if usage_count >= settings.scan_daily_quota:
            raise HTTPException(status_code=429, detail=ERROR_SCAN_DAILY_QUOTA)

        window = _SCAN_RATE_WINDOWS[user_id]
        cutoff = now_ts - settings.scan_rate_limit_window_seconds
        _prune_window(window, cutoff)

        if len(window) >= settings.scan_rate_limit_per_minute:
            retry_after = max(1, int(settings.scan_rate_limit_window_seconds - (now_ts - window[0])))
            raise HTTPException(
                status_code=429,
                detail=ERROR_SCAN_RATE_LIMIT,
                headers={"Retry-After": str(retry_after)},
            )

        window.append(now_ts)
        _SCAN_DAILY_USAGE[user_id] = (usage_day, usage_count + 1)


def enforce_auth_limits(remote_ip: str, identity: str) -> None:
    settings = get_settings()
    now_ts = time.time()

    ip_key = (remote_ip or "unknown").strip() or "unknown"
    identity_key = _normalize_identity(identity)

    with _LOCK:
        ip_window = _AUTH_RATE_WINDOWS_BY_IP[ip_key]
        ip_cutoff = now_ts - settings.auth_rate_limit_window_seconds
        _prune_window(ip_window, ip_cutoff)

        if len(ip_window) >= settings.auth_rate_limit_per_ip:
            retry_after = max(1, int(settings.auth_rate_limit_window_seconds - (now_ts - ip_window[0])))
            logger.warning("Auth rate limit exceeded for ip=%s", ip_key)
            raise HTTPException(
                status_code=429,
                detail=ERROR_AUTH_RATE_LIMIT,
                headers={"Retry-After": str(retry_after)},
            )

        ip_window.append(now_ts)

        if not identity_key:
            return

        locked_until = _AUTH_LOCKED_UNTIL.get(identity_key, 0.0)
        if locked_until > now_ts:
            retry_after = max(1, int(locked_until - now_ts))
            logger.warning(
                "Auth lockout active for identity=%s ip=%s retry_after=%s",
                _fingerprint(identity_key),
                ip_key,
                retry_after,
            )
            raise HTTPException(
                status_code=429,
                detail=ERROR_AUTH_LOCKED,
                headers={"Retry-After": str(retry_after)},
            )

        identity_window = _AUTH_RATE_WINDOWS_BY_IDENTITY[identity_key]
        identity_cutoff = now_ts - settings.auth_rate_limit_window_seconds
        _prune_window(identity_window, identity_cutoff)

        if len(identity_window) >= settings.auth_rate_limit_per_identity:
            retry_after = max(
                1,
                int(settings.auth_rate_limit_window_seconds - (now_ts - identity_window[0])),
            )
            logger.warning(
                "Auth rate limit exceeded for identity=%s ip=%s",
                _fingerprint(identity_key),
                ip_key,
            )
            raise HTTPException(
                status_code=429,
                detail=ERROR_AUTH_RATE_LIMIT,
                headers={"Retry-After": str(retry_after)},
            )

        identity_window.append(now_ts)


def register_auth_failure(remote_ip: str, identity: str) -> None:
    settings = get_settings()
    identity_key = _normalize_identity(identity)
    if not identity_key:
        return

    ip_key = (remote_ip or "unknown").strip() or "unknown"

    with _LOCK:
        failures = _AUTH_FAILURE_STREAK.get(identity_key, 0) + 1
        _AUTH_FAILURE_STREAK[identity_key] = failures

        if failures < settings.auth_lockout_threshold:
            return

        exponent = failures - settings.auth_lockout_threshold
        lockout_seconds = min(
            settings.auth_lockout_max_seconds,
            settings.auth_lockout_base_seconds * (2 ** exponent),
        )
        _AUTH_LOCKED_UNTIL[identity_key] = time.time() + lockout_seconds

    logger.warning(
        "Auth lockout applied for identity=%s ip=%s failures=%s lockout_seconds=%s",
        _fingerprint(identity_key),
        ip_key,
        failures,
        lockout_seconds,
    )


def register_auth_success(identity: str) -> None:
    identity_key = _normalize_identity(identity)
    if not identity_key:
        return

    with _LOCK:
        _AUTH_FAILURE_STREAK.pop(identity_key, None)
        _AUTH_LOCKED_UNTIL.pop(identity_key, None)


def reset_scan_limits_for_tests() -> None:
    with _LOCK:
        _SCAN_RATE_WINDOWS.clear()
        _SCAN_DAILY_USAGE.clear()
        _AUTH_RATE_WINDOWS_BY_IP.clear()
        _AUTH_RATE_WINDOWS_BY_IDENTITY.clear()
        _AUTH_FAILURE_STREAK.clear()
        _AUTH_LOCKED_UNTIL.clear()