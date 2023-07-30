import spy
import json

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