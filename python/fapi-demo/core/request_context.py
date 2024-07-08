from contextvars import ContextVar
from typing import Any
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

#request scoped storage
request_context_var: ContextVar[dict] = ContextVar("request_context", default={})

#middleware
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        context = {
            "request_id": str(uuid4()),
        }
        token = request_context_var.set(context)
        try:
            response = await call_next(request)
            return response
        finally:
            request_context_var.reset(token)


def getRequestContext() -> dict[str, Any]:
    return request_context_var.get()

def getPublicRequestContext() -> dict[str, Any]:
    request_context = getRequestContext()  
    public_context = {}
    for key, value in request_context.items():
        if not key.startswith("_"):
            public_context[key] = value
    return public_context

def getContext(key: str, default=None):
    ctx = request_context_var.get()
    return ctx.get(key, default)

def setContext(key: str, value: Any):
    ctx = request_context_var.get()
    ctx[key] = value
    request_context_var.set(ctx)

if __name__ == "__main__":
    ctx = getRequestContext()
    print(ctx)

    setContext('uid', 101)
    setContext('req_id', 9001)
    ctx = getRequestContext()
    print(ctx)

    setContext('orderId', 123)
    ctx = getRequestContext()
    print(ctx)