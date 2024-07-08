from logging import Logger
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from core import logger
from core.app import getApp
from core.request_context import RequestContextMiddleware

from core.resource_loader import getResourceLoader
from core.reply import Reply
from core.exception import UserException

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
async def default_exception_handler(request: Request, ex: Exception):
    message = type(ex).__name__ + ': ' +  str(ex)
    code = 500

    at = ''
    if hasattr(ex, 'at'):
        at = str(ex.at) # type: ignore
   
    #log error
    getLogger().error(message + ' @' + str(at))
    return Reply.json_response(code, message, Reply.code_to_str(code), None, {
        'at': at,
    })

def getLogger() -> Logger: 
    return logger.getLogger('err500')