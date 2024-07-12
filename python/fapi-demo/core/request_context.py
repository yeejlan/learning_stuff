from contextvars import ContextVar
from typing import Any, Dict
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.uuid_helper import uuid_to_base58

#request scoped storage
request_context_var: ContextVar[dict] = ContextVar("request_context", default={})

#middleware
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ctx = request_context_var.get()
        ctx['request_id'] = uuid_to_base58(uuid4())
        token = request_context_var.set(ctx)
        try:
            response = await call_next(request)
            return response
        finally:
            request_context_var.reset(token)


def getRequestContextDict() -> dict[str, Any]:
    return request_context_var.get()

def getPublicRequestContext() -> dict[str, Any]:
    request_context = getRequestContextDict()  
    public_context = {}
    for key, value in request_context.items():
        if not key.startswith("_"):
            public_context[key] = value
    return public_context

def getRequestContext(key: str, default=None):
    ctx = request_context_var.get()
    return ctx.get(key, default)

def setRequestContext(key: str, value: Any):
    ctx = request_context_var.get()
    ctx[key] = value
    request_context_var.set(ctx)

def setRequestContextViaDict(data: Dict = {}):
    ctx = request_context_var.get()
    for key in data:
        ctx[key] = data[key]
    request_context_var.set(ctx)    


if __name__ == "__main__":
    ctx = getRequestContextDict()
    print(ctx)

    setRequestContext('uid', 101)
    setRequestContext('req_id', 9001)
    ctx = getRequestContextDict()
    print(ctx)

    setRequestContext('orderId', 123)
    ctx = getRequestContextDict()
    print(ctx)