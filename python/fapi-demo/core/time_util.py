
from datetime import datetime, timezone

import arrow


fallback_tz=datetime.now().astimezone().tzinfo

def fallback_to_local_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=fallback_tz)
    return dt

def now_as_datetime() -> datetime:
    now = arrow.now().datetime
    return now

def now_as_iso8601(with_microseconds: bool = True) -> str:
    now = arrow.now().datetime
    if not with_microseconds:
        now = now.replace(microsecond=0)

    return now.isoformat()


def now_with_timezone(tz: timezone = timezone.utc) -> datetime:
    now = datetime.now(tz)
    return now

def now_as_iso8601_with_timezone(tz: timezone = timezone.utc, with_microseconds: bool = True) -> str:
    now = now_with_timezone(tz)
    if not with_microseconds:
        now = now.replace(microsecond=0)

    return now.isoformat()


def now_as_mysql_datetime() -> str:
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')