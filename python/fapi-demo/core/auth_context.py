from collections import UserDict
import sys, os

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from core.config import getConfig
from contextvars import ContextVar
from typing import Any

from core.request_context import getRequestContext
from starlette.requests import Request as StarRequest

auth_context_var: ContextVar[dict] = ContextVar("auth_context")

config = getConfig()
is_debug = config.getBool('APP_DEBUG', False)

#middleware
class AuthContextAsgiMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        ctx = {}
        if is_debug:
            request = StarRequest(scope)
            user_id = request.query_params.get('_user_id', None)
            skip_auth = request.query_params.get('_skip_auth', None)
            if user_id and skip_auth:
                ctx['user_id'] = user_id
                getRequestContext()['user_id'] = user_id

        token = auth_context_var.set(ctx)
        try:
            await self.app(scope, receive, send)
        finally:
            auth_context_var.reset(token)


class AuthContextException(Exception):
    pass

class AuthContext(UserDict):
    def __init__(self, *args: Any, **kwargs: Any):
        # not calling super on purpose
        if args or kwargs:
            raise AuthContextException("Please use middleware to initial auth_context")

    @property
    def data(self) -> dict:
        try:
            return auth_context_var.get()
        except LookupError:
            raise AuthContextException('Please use middleware to initial auth_context')

    def __repr__(self) -> str:
        try:
            return f"<{__name__}.{self.__class__.__name__} {self.data}>"
        except AuthContextException:
            return f"<{__name__}.{self.__class__.__name__} {dict()}>"

    def __str__(self):
        try:
            return str(self.data)
        except AuthContextException:
            return str({})


auth_context = AuthContext()

def getAuthContext():
    return auth_context

def getUserId() -> int:
    uid = auth_context.get('user_id', '0')
    return int(uid)

def setUserId(user_id: int):
    auth_context['user_id'] = user_id


if __name__ == "__main__":
    auth_context_var.set({'role': 'admin'})

    setUserId(100123)
    ctx = getAuthContext()
    ctx['name'] = 'NaNa'
    print(auth_context)

    userid = getUserId()
    print(userid)
