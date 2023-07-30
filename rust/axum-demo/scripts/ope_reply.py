import spy
import json

SUCCESS = 0;
BAD_RESULT = 1000;
BAD_TOKEN = 1100;
BAD_PARAM = 1200;
OPERATION_NOT_ALLOWED = 1300;
RESOURCE_NOT_FOUND = 1400;
OPERATION_FAILED = 1500;
OPERATION_PENDING = 1600;   

def success(data) -> spy.SpyResponse: 
    
    payload = {
        "code": 0,
        "data": data,
        "message": "success",
        "reason": "success",
    }

    resp = spy.SpyResponse()
    resp.headers = {"content-type": "application/json"}
    resp.content = json.dumps(payload)
    return resp

def failed(message: str, code: int) -> spy.SpyResponse: 

    payload = {
        "code": code,
        "data": None,
        "message": message,
        "reason": code_to_reason(code),
    }
  
    resp = spy.SpyResponse()
    resp.headers = {"content-type": "application/json"}
    resp.content = json.dumps(payload)
    return resp

def code_to_reason(code: int) -> str:
    return spy.code_to_reason(code)