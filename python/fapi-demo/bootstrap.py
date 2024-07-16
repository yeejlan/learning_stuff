from fastapi.exceptions import RequestValidationError
from core import logger
from core.app import getApp
from core.auth_context import AuthContextAsgiMiddleware
from core.cache import RefreshCacheAsgiMiddleware
from core.request_context import RequestContextAsgiMiddleware
from core.exception import ExceptionHandlerAsgiMiddleware, validation_exception_handler

app = getApp()

logger.buildInitialLoggers(['app', 'err500'])


app.add_middleware(ExceptionHandlerAsgiMiddleware)
app.add_middleware(AuthContextAsgiMiddleware)
app.add_middleware(RequestContextAsgiMiddleware)
app.add_middleware(RefreshCacheAsgiMiddleware)
 

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, ex):
    return validation_exception_handler(ex)

