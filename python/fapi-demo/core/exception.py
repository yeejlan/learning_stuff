import sys, os

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