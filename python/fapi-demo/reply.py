from enum import IntEnum

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
        return Reply.__str_map[self.value]
    
    def __int__(self):
        return self.value


    @staticmethod
    def success(resp: any):
        j = {
            'code': 0,
            'message': 'success',
            'reason': 'success',
            'data': resp,
        }
        return j


    @staticmethod
    def failed(message: str, code: int): 
        j = {
            'code': code,
            'message': message,
            'reason': Reply.code_to_str(code),
            'data': None,
        }
        return j


    @staticmethod
    def code_to_str(code: int) -> str:
        return Reply.__str_map[code]


    @staticmethod
    def status_code(code: int) -> int:
        c: int = 200
        #Status code values in the range 100-999 (inclusive) are supported
        if code >= 100 and code < 1000 :
            c = code

        return c
