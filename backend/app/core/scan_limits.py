from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import hashlib
import logging
import math
from threading import Lock
import time
from typing import Protocol
import uuid

from fastapi import HTTPException

from app.core.client_ip import UNKNOWN_REMOTE_IP, validate_trusted_proxy_startup_configuration
from app.core.config import Settings, get_settings
from app.core.constants import (
    ERROR_AUTH_LOCKED,
    ERROR_AUTH_RATE_LIMIT,
    ERROR_RATE_LIMIT_BACKEND_UNAVAILABLE,
    ERROR_SCAN_DAILY_QUOTA,
    ERROR_SCAN_RATE_LIMIT,
)

try:
    from redis import Redis
    from redis.exceptions import RedisError
except Exception:  # pragma: no cover - import errors are handled by runtime validation.
    Redis = None  # type: ignore[assignment]

    class RedisError(Exception):
        """Fallback RedisError type used when redis dependency is unavailable."""

        pass

logger = logging.getLogger(__name__)


class RateLimitStore(Protocol):
    def validate_connection(self) -> None:
        ...

    def enforce_scan_limits(self, user_id: str, settings: Settings) -> None:
        ...

    def enforce_auth_limits(self, remote_ip: str, identity: str, settings: Settings) -> None:
        ...

    def register_auth_failure(self, remote_ip: str, identity: str, settings: Settings) -> None:
        ...

    def register_auth_success(self, identity: str) -> None:
        ...

    def reset(self) -> None:
        ...


class InMemoryRateLimitStore:
    def __init__(self) -> None:
        self._scan_rate_windows: dict[str, deque[float]] = defaultdict(deque)
        self._scan_daily_usage: dict[str, tuple[str, int]] = {}
        self._auth_rate_windows_by_ip: dict[str, deque[float]] = defaultdict(deque)
        self._auth_rate_windows_by_identity: dict[str, deque[float]] = defaultdict(deque)
        self._auth_failure_streak: dict[str, int] = defaultdict(int)
        self._auth_locked_until: dict[str, float] = {}
        self._lock = Lock()

    def validate_connection(self) -> None:
        return

    def enforce_scan_limits(self, user_id: str, settings: Settings) -> None:
        now_ts = time.time()
        today = _current_utc_day()

        with self._lock:
            usage_day, usage_count = self._scan_daily_usage.get(user_id, (today, 0))
            if usage_day != today:
                usage_day, usage_count = today, 0

            if usage_count >= settings.scan_daily_quota:
                raise HTTPException(status_code=429, detail=ERROR_SCAN_DAILY_QUOTA)

            window = self._scan_rate_windows[user_id]
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
            self._scan_daily_usage[user_id] = (usage_day, usage_count + 1)

    def enforce_auth_limits(self, remote_ip: str, identity: str, settings: Settings) -> None:
        now_ts = time.time()

        ip_key = _normalize_remote_ip_bucket(remote_ip)
        identity_key = _normalize_identity(identity)

        with self._lock:
            ip_window = self._auth_rate_windows_by_ip[ip_key]
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

            locked_until = self._auth_locked_until.get(identity_key, 0.0)
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

            identity_window = self._auth_rate_windows_by_identity[identity_key]
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

    def register_auth_failure(self, remote_ip: str, identity: str, settings: Settings) -> None:
        identity_key = _normalize_identity(identity)
        if not identity_key:
            return

        ip_key = _normalize_remote_ip_bucket(remote_ip)

        with self._lock:
            failures = self._auth_failure_streak.get(identity_key, 0) + 1
            self._auth_failure_streak[identity_key] = failures

            if failures < settings.auth_lockout_threshold:
                return

            exponent = failures - settings.auth_lockout_threshold
            lockout_seconds = min(
                settings.auth_lockout_max_seconds,
                settings.auth_lockout_base_seconds * (2 ** exponent),
            )
            self._auth_locked_until[identity_key] = time.time() + lockout_seconds

        logger.warning(
            "Auth lockout applied for identity=%s ip=%s failures=%s lockout_seconds=%s",
            _fingerprint(identity_key),
            ip_key,
            failures,
            lockout_seconds,
        )

    def register_auth_success(self, identity: str) -> None:
        identity_key = _normalize_identity(identity)
        if not identity_key:
            return

        with self._lock:
            self._auth_failure_streak.pop(identity_key, None)
            self._auth_locked_until.pop(identity_key, None)

    def reset(self) -> None:
        with self._lock:
            self._scan_rate_windows.clear()
            self._scan_daily_usage.clear()
            self._auth_rate_windows_by_ip.clear()
            self._auth_rate_windows_by_identity.clear()
            self._auth_failure_streak.clear()
            self._auth_locked_until.clear()


class RedisRateLimitStore:
    _WINDOW_SCRIPT = """
local key = KEYS[1]
local now_ms = tonumber(ARGV[1])
local window_ms = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local ttl = tonumber(ARGV[4])
local member = ARGV[5]

redis.call('ZREMRANGEBYSCORE', key, 0, now_ms - window_ms)
local count = redis.call('ZCARD', key)
if count >= limit then
  local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
  local retry_ms = window_ms
  if oldest[2] then
    retry_ms = math.max(1, window_ms - (now_ms - tonumber(oldest[2])))
  end
  return {0, retry_ms}
end

redis.call('ZADD', key, now_ms, member)
redis.call('EXPIRE', key, ttl)
return {1, 0}
"""

    _SCAN_SCRIPT = """
local window_key = KEYS[1]
local quota_key = KEYS[2]

local now_ms = tonumber(ARGV[1])
local window_ms = tonumber(ARGV[2])
local rate_limit = tonumber(ARGV[3])
local quota_limit = tonumber(ARGV[4])
local window_ttl = tonumber(ARGV[5])
local quota_ttl = tonumber(ARGV[6])
local member = ARGV[7]

redis.call('ZREMRANGEBYSCORE', window_key, 0, now_ms - window_ms)
local window_count = redis.call('ZCARD', window_key)
if window_count >= rate_limit then
  local oldest = redis.call('ZRANGE', window_key, 0, 0, 'WITHSCORES')
  local retry_ms = window_ms
  if oldest[2] then
    retry_ms = math.max(1, window_ms - (now_ms - tonumber(oldest[2])))
  end
  return {0, retry_ms, 0}
end

local daily_count = tonumber(redis.call('GET', quota_key) or '0')
if daily_count >= quota_limit then
  return {2, 0, daily_count}
end

redis.call('ZADD', window_key, now_ms, member)
redis.call('EXPIRE', window_key, window_ttl)
daily_count = redis.call('INCR', quota_key)
if daily_count == 1 then
  redis.call('EXPIRE', quota_key, quota_ttl)
end
return {1, 0, daily_count}
"""

    def __init__(self, redis_url: str, key_prefix: str) -> None:
        if Redis is None:
            raise RuntimeError(
                "redis dependency is not installed. Install redis package to use RATE_LIMIT_STORE=redis."
            )
        self._client = Redis.from_url(redis_url, decode_responses=True)
        self._key_prefix = key_prefix.rstrip(":")

    def validate_connection(self) -> None:
        try:
            self._client.ping()
        except RedisError as error:
            raise RuntimeError("Redis connection failed for rate limiting.") from error

    def enforce_scan_limits(self, user_id: str, settings: Settings) -> None:
        now_ms = int(time.time() * 1000)
        window_ms = settings.scan_rate_limit_window_seconds * 1000
        window_ttl = max(settings.scan_rate_limit_window_seconds + 60, 60)
        quota_ttl = max(_seconds_until_next_utc_day() + 3600, 7200)
        member = f"{now_ms}-{uuid.uuid4().hex[:12]}"

        user_bucket = _storage_bucket(user_id)
        window_key = self._key("scan", "window", user_bucket)
        quota_key = self._key("scan", "daily", user_bucket, _current_utc_day())

        try:
            result = self._client.eval(
                self._SCAN_SCRIPT,
                2,
                window_key,
                quota_key,
                now_ms,
                window_ms,
                settings.scan_rate_limit_per_minute,
                settings.scan_daily_quota,
                window_ttl,
                quota_ttl,
                member,
            )
        except RedisError as error:
            logger.exception("Redis scan limit check failed: %s", error)
            _raise_rate_limit_backend_unavailable()

        status = int(result[0])
        retry_ms = int(result[1])

        if status == 0:
            retry_after = _retry_after_seconds_from_ms(retry_ms)
            raise HTTPException(
                status_code=429,
                detail=ERROR_SCAN_RATE_LIMIT,
                headers={"Retry-After": str(retry_after)},
            )

        if status == 2:
            raise HTTPException(status_code=429, detail=ERROR_SCAN_DAILY_QUOTA)

        if status != 1:
            logger.error("Unexpected Redis scan limit script status=%s", status)
            _raise_rate_limit_backend_unavailable()

    def enforce_auth_limits(self, remote_ip: str, identity: str, settings: Settings) -> None:
        ip_key = _normalize_remote_ip_bucket(remote_ip)
        identity_key = _normalize_identity(identity)

        ip_window_key = self._key("auth", "ip", _storage_bucket(ip_key), "window")
        allowed_ip, retry_after = self._check_and_increment_window(
            key=ip_window_key,
            limit=settings.auth_rate_limit_per_ip,
            window_seconds=settings.auth_rate_limit_window_seconds,
        )
        if not allowed_ip:
            logger.warning("Auth rate limit exceeded for ip=%s", ip_key)
            raise HTTPException(
                status_code=429,
                detail=ERROR_AUTH_RATE_LIMIT,
                headers={"Retry-After": str(retry_after)},
            )

        if not identity_key:
            return

        identity_bucket = _storage_bucket(identity_key)
        lock_key = self._key("auth", "identity", identity_bucket, "lock_until_ms")
        now_ms = int(time.time() * 1000)

        try:
            locked_until_ms_raw = self._client.get(lock_key)
            locked_until_ms = int(locked_until_ms_raw) if locked_until_ms_raw else 0
        except (RedisError, ValueError) as error:
            logger.exception("Redis auth lockout lookup failed: %s", error)
            _raise_rate_limit_backend_unavailable()

        if locked_until_ms > now_ms:
            retry_after = _retry_after_seconds_from_ms(locked_until_ms - now_ms)
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

        identity_window_key = self._key("auth", "identity", identity_bucket, "window")
        allowed_identity, retry_after = self._check_and_increment_window(
            key=identity_window_key,
            limit=settings.auth_rate_limit_per_identity,
            window_seconds=settings.auth_rate_limit_window_seconds,
        )
        if not allowed_identity:
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

    def register_auth_failure(self, remote_ip: str, identity: str, settings: Settings) -> None:
        identity_key = _normalize_identity(identity)
        if not identity_key:
            return

        ip_key = _normalize_remote_ip_bucket(remote_ip)
        identity_bucket = _storage_bucket(identity_key)
        failures_key = self._key("auth", "identity", identity_bucket, "failures")
        lock_key = self._key("auth", "identity", identity_bucket, "lock_until_ms")

        try:
            failures = int(self._client.incr(failures_key))
            failure_ttl_seconds = max(
                settings.auth_lockout_max_seconds * 4,
                settings.auth_rate_limit_window_seconds * 2,
                600,
            )
            self._client.expire(failures_key, failure_ttl_seconds)
        except RedisError as error:
            logger.exception("Redis auth failure tracking failed: %s", error)
            return

        if failures < settings.auth_lockout_threshold:
            return

        exponent = failures - settings.auth_lockout_threshold
        lockout_seconds = min(
            settings.auth_lockout_max_seconds,
            settings.auth_lockout_base_seconds * (2 ** exponent),
        )
        locked_until_ms = int(time.time() * 1000) + (lockout_seconds * 1000)

        try:
            self._client.set(lock_key, locked_until_ms, ex=lockout_seconds + 60)
        except RedisError as error:
            logger.exception("Redis auth lockout write failed: %s", error)
            return

        logger.warning(
            "Auth lockout applied for identity=%s ip=%s failures=%s lockout_seconds=%s",
            _fingerprint(identity_key),
            ip_key,
            failures,
            lockout_seconds,
        )

    def register_auth_success(self, identity: str) -> None:
        identity_key = _normalize_identity(identity)
        if not identity_key:
            return

        identity_bucket = _storage_bucket(identity_key)
        failures_key = self._key("auth", "identity", identity_bucket, "failures")
        lock_key = self._key("auth", "identity", identity_bucket, "lock_until_ms")

        try:
            self._client.delete(failures_key, lock_key)
        except RedisError as error:
            logger.warning("Redis auth success cleanup failed: %s", error)

    def reset(self) -> None:
        try:
            pattern = self._key("*")
            keys = list(self._client.scan_iter(match=pattern, count=500))
            if keys:
                self._client.delete(*keys)
        except RedisError as error:
            logger.warning("Redis rate-limit reset failed: %s", error)

    def _key(self, *parts: str) -> str:
        return ":".join([self._key_prefix, *parts])

    def _check_and_increment_window(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now_ms = int(time.time() * 1000)
        window_ms = window_seconds * 1000
        ttl_seconds = max(window_seconds + 60, 60)
        member = f"{now_ms}-{uuid.uuid4().hex[:12]}"

        try:
            result = self._client.eval(
                self._WINDOW_SCRIPT,
                1,
                key,
                now_ms,
                window_ms,
                limit,
                ttl_seconds,
                member,
            )
        except RedisError as error:
            logger.exception("Redis window check failed: %s", error)
            _raise_rate_limit_backend_unavailable()

        allowed = int(result[0]) == 1
        retry_after = _retry_after_seconds_from_ms(int(result[1]))
        return allowed, retry_after


def _current_utc_day() -> str:
    return datetime.now(tz=timezone.utc).date().isoformat()


def _seconds_until_next_utc_day() -> int:
    now = datetime.now(tz=timezone.utc)
    next_day = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    return max(1, int((next_day - now).total_seconds()))


def _prune_window(window: deque[float], cutoff: float) -> None:
    while window and window[0] <= cutoff:
        window.popleft()


def _normalize_identity(identity: str | None) -> str:
    return (identity or "").strip().lower()


def _fingerprint(identity: str) -> str:
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]


def _normalize_remote_ip_bucket(remote_ip: str | None) -> str:
    return (remote_ip or UNKNOWN_REMOTE_IP).strip() or UNKNOWN_REMOTE_IP


def _storage_bucket(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _retry_after_seconds_from_ms(retry_ms: int) -> int:
    return max(1, math.ceil(max(1, retry_ms) / 1000))


def _raise_rate_limit_backend_unavailable() -> None:
    raise HTTPException(status_code=503, detail=ERROR_RATE_LIMIT_BACKEND_UNAVAILABLE)


_STORE_SELECTION_LOCK = Lock()
_ACTIVE_STORE: RateLimitStore | None = None
_ACTIVE_STORE_SIGNATURE: tuple[str, str | None, str] | None = None


def _build_rate_limit_store(settings: Settings) -> RateLimitStore:
    if settings.rate_limit_store == "redis":
        redis_url = (settings.redis_url or "").strip()
        if not redis_url:
            raise RuntimeError("RATE_LIMIT_STORE is redis but REDIS_URL is missing.")
        return RedisRateLimitStore(redis_url=redis_url, key_prefix=settings.redis_key_prefix)

    return InMemoryRateLimitStore()


def _get_rate_limit_store() -> RateLimitStore:
    global _ACTIVE_STORE, _ACTIVE_STORE_SIGNATURE

    settings = get_settings()
    signature = (settings.rate_limit_store, settings.redis_url, settings.redis_key_prefix)

    with _STORE_SELECTION_LOCK:
        if _ACTIVE_STORE is None or _ACTIVE_STORE_SIGNATURE != signature:
            _ACTIVE_STORE = _build_rate_limit_store(settings)
            _ACTIVE_STORE_SIGNATURE = signature
        return _ACTIVE_STORE


def validate_auth_limits_startup_configuration() -> None:
    settings = get_settings()
    settings.validate_rate_limit_configuration()
    validate_trusted_proxy_startup_configuration(
        app_env=settings.app_env,
        trusted_proxy_cidrs=settings.trusted_proxy_cidrs,
    )
    _get_rate_limit_store().validate_connection()


def enforce_scan_limits(user_id: str) -> None:
    settings = get_settings()
    _get_rate_limit_store().enforce_scan_limits(user_id=user_id, settings=settings)


def enforce_auth_limits(remote_ip: str, identity: str) -> None:
    settings = get_settings()
    _get_rate_limit_store().enforce_auth_limits(remote_ip=remote_ip, identity=identity, settings=settings)


def register_auth_failure(remote_ip: str, identity: str) -> None:
    settings = get_settings()
    _get_rate_limit_store().register_auth_failure(remote_ip=remote_ip, identity=identity, settings=settings)


def register_auth_success(identity: str) -> None:
    _get_rate_limit_store().register_auth_success(identity=identity)


def reset_scan_limits_for_tests() -> None:
    global _ACTIVE_STORE, _ACTIVE_STORE_SIGNATURE

    with _STORE_SELECTION_LOCK:
        store = _ACTIVE_STORE
        _ACTIVE_STORE = None
        _ACTIVE_STORE_SIGNATURE = None

    if store is not None:
        store.reset()