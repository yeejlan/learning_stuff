
import ope

def err500_action(req):
    raise ope.ServiceException("my service is down!")

def user_error_action(req):
    raise ope.UserException("messsage from user_error_action", ope.OPERATION_FAILED)

def req_info_action(req):
    return ope.success({
        'controller': req.controller,
        'action': req.action,
        'path': req.path,
        'query': req.query,
        'method': req.method,
        'headers': req.headers,
    })

def json_action(req):
    payload = ope.json_decode(req.body)
    return ope.success(payload)