from contextvars import ContextVar
from typing import Any
from uuid import uuid4
from fastapi import Request


#request scoped storage
request_context_var: ContextVar[dict] = ContextVar("request_context", default={})

#middleware
async def requestContextMiddleware(request: Request, call_next):
    context = {
        "request_id": str(uuid4()),
    }
    token = request_context_var.set(context)
    try:
        response = await call_next(request)
        return response
    finally:
        request_context_var.reset(token)


def get_request_context() -> dict[str, Any]:
    return request_context_var.get()