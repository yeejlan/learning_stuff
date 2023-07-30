import spy
import json

def success(data) -> spy.SpyResponse: 
    resp = spy.SpyResponse()
    resp.content = json.dumps(data)
    return resp

def failed(message: str, code: int) -> spy.SpyResponse: 
    resp = spy.SpyResponse()
    resp.content = json.dumps(None)
    return resp    