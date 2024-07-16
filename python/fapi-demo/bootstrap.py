from core import logger
from core.app import getApp
from core.auth_context import AuthContextAsgiMiddleware
from core.cache import CacheRefreshAsgiMiddleware
from core.request_context import RequestContextAsgiMiddleware
from core.exception import ExceptionHandlerAsgiMiddleware

app = getApp()

logger.buildInitialLoggers(['app', 'err500'])


app.add_middleware(ExceptionHandlerAsgiMiddleware)
app.add_middleware(AuthContextAsgiMiddleware)
app.add_middleware(RequestContextAsgiMiddleware)
app.add_middleware(CacheRefreshAsgiMiddleware)
 
