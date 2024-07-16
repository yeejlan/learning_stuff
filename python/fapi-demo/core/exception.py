from logging import Logger
import sys, os

from fastapi import Response
from fastapi.exceptions import RequestValidationError

from core import logger
from core.reply import Reply
from core.util import format_exception

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from core.config import getConfig
from collections import namedtuple
from typing import Any

config = getConfig()    
is_debug = config.getBool('APP_DEBUG', False)

FrameInfo = namedtuple('FrameInfo', ['file', 'line', 'func'])

def __str__(self):
    return f'{self.file}:{self.line}:{self.func}()'

FrameInfo.__str__ = __str__ 

def get_frame_info(look_back =2) -> FrameInfo:
    frame = sys._getframe(look_back)
    line = frame.f_lineno
    file = frame.f_code.co_filename
    file = file.lstrip(working_path)
    func = frame.f_code.co_name
    return FrameInfo(file, line, func)

class UserException(Exception):
    def __init__(self, message: str, code: int = 1000, extra: dict[str, Any] = {}, at: FrameInfo|None=None): 
        self.code = code
        self.message = message
        self.extra = extra
        self.at = at
        if not is_debug:
            return
        self.at = get_frame_info() if at is None else at

class FluxException(Exception):
    def __init__(self, message: str, at: FrameInfo|None=None):
        self.message = message
        self.at = at
        if not is_debug:
            return 
        self.at = get_frame_info() if at is None else at

class ServiceException(FluxException):
    pass

class ModelException(FluxException):
    pass

class ExceptionHandlerAsgiMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except UserException as ex:
            response = user_exception_handler(ex)
            await response(scope, receive, send)
        except RequestValidationError as ex:
            response = validation_exception_handler(ex)
            await response(scope, receive, send)
        except Exception as ex:
            response = default_exception_handler(ex)
            await response(scope, receive, send)


def user_exception_handler(ex: UserException) -> Response:
    code = ex.code
    message = ex.message
    extra = {} if ex.extra is None else ex.extra
    return Reply.json_response(code, message, Reply.code_to_str(code), None, extra)


def validation_exception_handler(ex: RequestValidationError) -> Response:
    code = Reply.BAD_PARAM
    err = ex.errors()[0]
    message = err['msg']
    
    err = {k: v for k, v in err.items() if k not in ('msg', 'input', 'url')}

    return Reply.json_response(code, message, Reply.code_to_str(code), None, {
        'error': err,
    })


def default_exception_handler(ex: Exception) -> Response:
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