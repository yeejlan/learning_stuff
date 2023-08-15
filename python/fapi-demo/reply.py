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
    BAD_RESULT = 1000
    BAD_TOKEN = 1100
    BAD_PARAM = 1200
    OPERATION_NOT_ALLOWED = 1300
    RESOURCE_NOT_FOUND = 1400
    OPERATION_FAILED = 1500
    OPERATION_PENDING = 1600

    __str_map = {
        401: 'unauthorized',
        403: 'forbidden',
        404: 'not_found',
        405: 'method_not_allowed',
        500: 'internal_server_error',

        SUCCESS: 'success',
        BAD_RESULT: 'bad_result',
        BAD_TOKEN: 'bad_token',
        BAD_PARAM: 'bad_param',
        OPERATION_NOT_ALLOWED: 'operation_not_allowed',
        RESOURCE_NOT_FOUND: 'resource_not_found',
        OPERATION_FAILED: 'operation_failed',
        OPERATION_PENDING: 'operation_pending',
    }

    def __str__(self):
        return Reply.__str_map[self.value] # type: ignore
    
    def __int__(self):
        return self.value


    @staticmethod
    def success(resp: Any):
        return Reply.json_response(0, 'success', 'success', resp)


    @staticmethod
    def failed(message: str, code: int): 
        return Reply.json_response(code, message, Reply.code_to_str(code), None)

    @staticmethod
    def redirect(url: str, status_code: int = 307):
        return RedirectResponse(url=url, status_code=status_code)

    @staticmethod
    def code_to_str(code: int) -> str:
        return Reply.__str_map[code] # type: ignore


    @staticmethod
    def status_code(code: int) -> int:
        c: int = 200
        #Status code values in the range 100-999 (inclusive) are supported
        if code >= 100 and code < 1000 :
            c = code

        return c
    
    @staticmethod
    def json_response(code:int, message:str, reason:str, data:Any, extra: dict = {}):

        # if isinstance(data, str):
        #     try:
        #         data = json.loads(data)
        #     except json.decoder.JSONDecodeError:
        #         pass

        status_code = Reply.status_code(code)
        content = {
            'code': code,
            'message': message,
            'reason': Reply.code_to_str(code),
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
    

class MyJsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.utcnow().isoformat()
        elif isinstance(o, BaseModel):
            if hasattr(o, 'api_dump'):
                return o.api_dump() # type: ignore
            return o.model_dump()

        return super().default(o)