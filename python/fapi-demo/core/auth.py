import sys, os

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from core.config import getConfig
from contextvars import ContextVar
from typing import Any, Dict
from starlette.middleware.base import BaseHTTPMiddleware

from core.request_context import setRequestContext

auth_context: ContextVar[dict] = ContextVar("auth_context", default={})

config = getConfig()
is_debug = config.getBool('APP_DEBUG', False)

#middleware
class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = auth_context.set({})
        user_id = request.query_params.get('_user_id', None)
        skip_auth = request.query_params.get('_skip_auth', None)
        ctx = {}
        if is_debug and user_id and skip_auth:
            ctx['user_id'] = user_id
            setRequestContext('user_id', user_id)
            auth_context.set(ctx)
        try:
            response = await call_next(request)
        finally:
            auth_context.reset(token)
        return response


def getLoggedinUserId() -> Any:
    return getAuthContext('user_id')

def setLoggedinUserId(user_id: Any):
    setRequestContext('user_id', user_id)
    setAuthContext('user_id', user_id)

def getAuthContextDict() -> dict[str, Any]:
    return auth_context.get()

def getAuthContext(key: str, default=None):
    ctx = auth_context.get()
    return ctx.get(key, default)

def setAuthContext(key: str, value: Any):
    ctx = auth_context.get()
    ctx[key] = value
    auth_context.set(ctx)

def setAuthContextViaDict(data: Dict = {}):
    ctx = auth_context.get()
    for key in data:
        ctx[key] = data[key]
    auth_context.set(ctx)


if __name__ == "__main__":
    auth_context.set({})

    setLoggedinUserId(100123)
    setAuthContext('rank', 30)
    auth_ctx = getAuthContextDict()
    print(auth_ctx)

    userid = getLoggedinUserId()
    print(userid)

