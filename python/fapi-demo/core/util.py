from datetime import datetime, timezone

def now_with_timezone(tz: timezone = timezone.utc) -> datetime:
    now = datetime.now(tz)
    return now

def now_as_iso8601(tz: timezone = timezone.utc, with_microseconds: bool = True) -> str:
    now = now_with_timezone(tz)
    if not with_microseconds:
        now = now.replace(microsecond=0)
    
    return now.isoformat()
