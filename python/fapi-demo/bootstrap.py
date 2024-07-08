from logging import Logger
import traceback
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from core import logger
from core.app import getApp
from core.request_context import RequestContextMiddleware

from core.resource_loader import getResourceLoader
from core.reply import Reply
from core.exception import FluxException, ModelException, UserException

app = getApp()
logger.buildInitialLoggers(['app', 'err500'])
app.add_middleware(RequestContextMiddleware)

@app.on_event("startup")
async def startup():
    await getResourceLoader().createMysqlPool('DB')

@app.on_event("shutdown")
async def shutdown():
    await getResourceLoader().closeMysqlPool('DB')

@app.exception_handler(UserException)
async def user_exception_handler(request: Request, ex: UserException):
    code = ex.code
    message = ex.message
    at = ex.at
    return Reply.json_response(code, message, Reply.code_to_str(code), None, {
        'at': str(at),
    })


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, ex):
    code = Reply.BAD_PARAM
    err = ex.errors()[0]
    message = err['msg']
    
    del err['msg']
    del err['input']
    del err['url']

    return Reply.json_response(code, message, Reply.code_to_str(code), None, {
        'error': err,
    })

@app.exception_handler(Exception)
@app.exception_handler(ModelException)
@app.exception_handler(FluxException)
async def default_exception_handler(request: Request, ex: Exception):
    message = f"{type(ex).__name__}: {str(ex)}"
    code = 500
    at = getattr(ex, 'at', '')

    stack_trace = traceback.format_exc().strip()
    error_log = f"{message} @{at}\n{stack_trace}"

    #log error
    getLogger().error(error_log)

    return Reply.json_response(code, message, Reply.code_to_str(code), None, {
        'at': at,
    })

def getLogger() -> Logger: 
    return logger.getLogger('err500')