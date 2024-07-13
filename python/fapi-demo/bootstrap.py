from logging import Logger
import traceback
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from core import logger
from core.app import getApp
from core.auth import AuthContextMiddleware
from core.cache import CacheRefreshMiddleware
from core.request_context import RequestContextMiddleware

from core.resource_loader import getResourceLoader
from core.reply import Reply
from core.exception import FluxException, ModelException, ServiceException, UserException
from core.user_session import UserSessionMiddleware
from core.util import format_exception

app = getApp()
logger.buildInitialLoggers(['app', 'err500'])
app.add_middleware(AuthContextMiddleware)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(UserSessionMiddleware)
app.add_middleware(CacheRefreshMiddleware)

@app.on_event("startup")
async def startup():
    await getResourceLoader().loadAll()

@app.on_event("shutdown")
async def shutdown():
    await getResourceLoader().releaseAll()

@app.exception_handler(UserException)
async def user_exception_handler(request: Request, ex: UserException):
    code = ex.code
    message = ex.message
    extra = {} if ex.extra is None else ex.extra
    extra['at'] = str(ex.at)
    return Reply.json_response(code, message, Reply.code_to_str(code), None, extra)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, ex):
    code = Reply.BAD_PARAM
    err = ex.errors()[0]
    message = err['msg']
    
    err = {k: v for k, v in err.items() if k not in ('msg', 'input', 'url')}

    return Reply.json_response(code, message, Reply.code_to_str(code), None, {
        'error': err,
    })

@app.exception_handler(Exception)
@app.exception_handler(FluxException)
async def default_exception_handler(request: Request, ex: Exception):
    message = f"{type(ex).__name__}: {str(ex)}"
    code = 500
    at = getattr(ex, 'at', '')

    error_log = format_exception(ex, full_stack=True)

    #log error
    getLogger().error(error_log)

    return Reply.json_response(code, message, Reply.code_to_str(code), None, {
        'at': at,
    })

def getLogger() -> Logger: 
    return logger.getLogger('err500')