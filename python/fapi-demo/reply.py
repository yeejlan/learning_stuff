from datetime import datetime
from enum import IntEnum
import json
from logging import Logger
from typing import Any
from fastapi import Response

from fastapi.responses import RedirectResponse
from pydantic import BaseModel

import log
class Reply(IntEnum):
    SUCCESS = 0
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500

    BAD_RESULT = 1000
    BAD_TOKEN = 1100
    BAD_PARAM = 1200
    OPERATION_NOT_ALLOWED = 1300
    RESOURCE_NOT_FOUND = 1400
    OPERATION_FAILED = 1500
    OPERATION_PENDING = 1600


    def __str__(self):
        return self.name.lower()
    
    def __int__(self):
        return self.value


    @classmethod
    def success(cls, resp: Any):
        return cls.json_response(0, 'success', 'success', resp)


    @classmethod
    def failed(cls, message: str, code: int): 
        return cls.json_response(code, message, Reply.code_to_str(code), None)

    @staticmethod
    def redirect(url: str, status_code: int = 307):
        return RedirectResponse(url=url, status_code=status_code)

    @staticmethod
    def code_to_str(code: int) -> str:
        return reply_map_reversed[code]


    @staticmethod
    def status_code(code: int) -> int:
        c: int = 200
        #Status code values in the range 100-999 (inclusive) are supported
        if code >= 100 and code < 1000 :
            c = code

        return c
    
    @classmethod
    def json_response(cls, code:int, message:str, reason:str, data:Any, extra: dict = {}):

        status_code = cls.status_code(code)
        content = {
            'code': code,
            'message': message,
            'reason': cls.code_to_str(code),
            'data': data,
        }
        if extra:
            content.update(extra)

        content = json.dumps(content, cls=MyJsonEncoder)
        return Response(
            status_code=status_code,
            content=content,
            media_type='application/json',
        )
    
    @staticmethod
    def get_logger(channel_name: str) -> Logger:
        return log.get_logger(channel_name)
    

reply_map = {member.name.lower(): member.value for member in Reply}
reply_map_reversed = {v: k for k, v in reply_map.items()}

class MyJsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.utcnow().isoformat()
        elif isinstance(o, BaseModel):
            if hasattr(o, 'api_dump'):
                return o.api_dump() # type: ignore
            return o.model_dump()

        return super().default(o)