
import spy
import ope

def err500_action(req: spy.SpyRequest) -> spy.SpyResponse:
    raise ope.ServiceException("my service is down!")

def user_error_action(req: spy.SpyRequest) -> spy.SpyResponse:
    raise ope.UserException("messsage from user_error_action", ope.OPERATION_FAILED)

def req_info_action(req: spy.SpyRequest) -> spy.SpyResponse:
    return ope.success({
        'controller': req.controller,
        'action': req.action,
        'path': req.path,
        'query': req.query,
        'method': req.method,
        'headers': req.headers,
    })

def json_action(req: spy.SpyRequest) -> spy.SpyResponse:
    payload = ope.json_decode(req.body)
    return ope.success(payload)