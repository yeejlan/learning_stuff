import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

T = TypeVar('T')

def now_with_timezone(tz: timezone = timezone.utc) -> datetime:
    now = datetime.now(tz)
    return now

def now_as_iso8601(tz: timezone = timezone.utc, with_microseconds: bool = True) -> str:
    now = now_with_timezone(tz)
    if not with_microseconds:
        now = now.replace(microsecond=0)
    
    return now.isoformat()

async def run_sync(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    # Execute synchronous function in a thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))