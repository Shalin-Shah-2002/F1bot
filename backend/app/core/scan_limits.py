from collections import defaultdict, deque
from datetime import datetime, timezone
from threading import Lock
import time

from fastapi import HTTPException

from app.core.config import get_settings
from app.core.constants import ERROR_SCAN_DAILY_QUOTA, ERROR_SCAN_RATE_LIMIT


_SCAN_RATE_WINDOWS: dict[str, deque[float]] = defaultdict(deque)
_SCAN_DAILY_USAGE: dict[str, tuple[str, int]] = {}
_LOCK = Lock()


def _current_utc_day() -> str:
    return datetime.now(tz=timezone.utc).date().isoformat()


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
        while window and window[0] <= cutoff:
            window.popleft()

        if len(window) >= settings.scan_rate_limit_per_minute:
            retry_after = max(1, int(settings.scan_rate_limit_window_seconds - (now_ts - window[0])))
            raise HTTPException(
                status_code=429,
                detail=ERROR_SCAN_RATE_LIMIT,
                headers={"Retry-After": str(retry_after)},
            )

        window.append(now_ts)
        _SCAN_DAILY_USAGE[user_id] = (usage_day, usage_count + 1)


def reset_scan_limits_for_tests() -> None:
    with _LOCK:
        _SCAN_RATE_WINDOWS.clear()
        _SCAN_DAILY_USAGE.clear()