from logging import Logger
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import log
import uuid
import db

from reply import Reply
from exception import UserException

# Create app
app = FastAPI(host="0.0.0.0",
              port=5000,
              title="My FastApi Demo",
              version="1.2.34",
            )

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    uuid_str = str(uuid.uuid4())
    log.request_id.set(uuid_str)
    response = await call_next(request)
    # response.headers['request-id'] = uuid_str
    return response

@app.on_event("startup")
async def startup():
    db.pool = await db.create_pool()

@app.on_event("shutdown")
async def shutdown():
    await db.release_pool()

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
    return log.get_logger('err500')