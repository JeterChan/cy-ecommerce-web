from datetime import datetime, timezone


def now_utc() -> datetime:
    """回傳當前的 UTC 時間"""
    return datetime.now(timezone.utc)
