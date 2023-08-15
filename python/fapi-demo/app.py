from logging import Logger
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import log
import uuid

from reply import Reply
from exception import UserException

from controllers import router


# Load env file
load_dotenv()

# Create app
app = FastAPI(host="0.0.0.0", port=5000)
app.include_router(router)
app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/")
async def homepage():
    return Reply.success("this is the homepage~")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    uuid_str = str(uuid.uuid4())
    log.request_id.set(uuid_str)
    response = await call_next(request)
    response.headers['request-id'] = uuid_str
    return response

@app.exception_handler(UserException)
async def user_exception_handler(request: Request, ex: UserException):
    code = ex.code
    message = ex.message
    return Reply.json_response(code, message, Reply.code_to_str(code), None)


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
    #log error
    getLogger().error(message)
    return Reply.json_response(code, message, Reply.code_to_str(code), None)

def getLogger() -> Logger: 
    return log.get_logger('err500')