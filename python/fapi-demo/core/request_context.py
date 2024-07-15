import sys, os

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from collections import UserDict
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

from core.uuid_helper import uuid_to_base58

#request scoped storage
request_context_var: ContextVar[dict] = ContextVar("request_context", default={})

class RequestContextException(Exception):
    pass

class RequestContext(UserDict):
    def __init__(self, *args: Any, **kwargs: Any):
        # not calling super on purpose
        if args or kwargs:
            raise RequestContextException("Please use middleware to initial request_context")

    @property
    def data(self) -> dict:
        try:
            return request_context_var.get()
        except LookupError:
            raise RequestContextException('Please use middleware to initial request_context')

    def __repr__(self) -> str:
        try:
            return f"<{__name__}.{self.__class__.__name__} {self.data}>"
        except RequestContextException:
            return f"<{__name__}.{self.__class__.__name__} {dict()}>"

    def __str__(self):
        try:
            return str(self.data)
        except RequestContextException:
            return str({})


request_context = RequestContext()

def getRequestContext():
    return request_context

def getRequestId() -> str:
    return request_context.get('request_id', '0000')

def setRequestId(request_id: str):
    request_context['request_id'] = request_id


#middleware
class RequestContextAsgiMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        ctx = {}
        ctx['request_id'] = uuid_to_base58(uuid4())
        token = request_context_var.set(ctx)
        try:
            await self.app(scope, receive, send)
        finally:
            request_context_var.reset(token)



if __name__ == "__main__":
    request_context_var.set({"a":1})

    ctx = getRequestContext()
    print(ctx)

    ctx['uid'] = 101
    ctx['req_id'] = 9001

    print(request_context)

    ctx['orderId'] = 123
    print(request_context)