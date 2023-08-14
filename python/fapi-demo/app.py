from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from reply import Reply
from exception import UserException

from controllers import router

app = FastAPI(host="0.0.0.0", port=5000)
app.include_router(router)

@app.get("/")
async def homepage():
    return Reply.success("this is the homepage~")

@app.exception_handler(UserException)
async def user_exception_handler(request: Request, ex: UserException):
    code = ex.code
    message = ex.message
    return Reply.json_response(code, message, Reply.code_to_str(code), None)

@app.exception_handler(Exception)
async def default_exception_handler(request: Request, ex: Exception):
    message = str(ex)
    code = 500
    return Reply.json_response(code, message, Reply.code_to_str(code), None)