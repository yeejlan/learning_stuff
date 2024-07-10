import sys
from collections import namedtuple
from typing import Any

FrameInfo = namedtuple('FrameInfo', ['file', 'line', 'func'])

def __str__(self):
    return f'{self.file}:{self.line}:{self.func}()'

FrameInfo.__str__ = __str__ 

def get_frame_info(look_back =2) -> FrameInfo:
    frame = sys._getframe(look_back)
    line = frame.f_lineno
    file = frame.f_code.co_filename
    func = frame.f_code.co_name
    return FrameInfo(file, line, func)

class UserException(Exception):
    def __init__(self, message: str, code: int = 1000, extra: dict[str, Any] = {}, at: FrameInfo|None=None): 
        self.code = code
        self.message = message
        self.extra = extra
        self.at = at
        if at is None:
            self.at = get_frame_info()

class ServiceException(Exception):
    def __init__(self, message: str, at: FrameInfo|None=None):
        self.message = message
        self.at = at
        if at is None:
            self.at = get_frame_info()

class ModelException(Exception):
    def __init__(self, message: str, at: FrameInfo|None=None):
        self.message = message
        self.at = at
        if at is None:
            self.at = get_frame_info()

class FluxException(Exception):
    def __init__(self, message: str, at: FrameInfo|None=None):
        self.message = message
        self.at = at
        if at is None:
            self.at = get_frame_info()
