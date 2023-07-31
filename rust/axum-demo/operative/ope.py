import ope_init as _
from ope_tracing import *
from ope_exception import *
from ope_reply import *
from spy import SpyRequest as Request, SpyResponse as Response
import importlib
from pathlib import Path

def json_decode(str_data: str): 
    try:
        data = json.loads(str_data)
    except json.JSONDecodeError as e:
        error_str = f"JSON Decode Error: {e.msg} on line {e.lineno}, column {e.colno}"        
        raise UserException(error_str, BAD_RESULT)
    return data


def handle_request(req: Request) -> Response:
    set_request_id(req.request_id())

    path = Path(req.path)
    controller = 'home'
    action = 'index'
    if(len(path.parts) == 1):  # "user"
        action = path.parts[0]
    
    if(len(path.parts) == 2): # "user/info"
        controller, action = path.parts

    if(len(path.parts) == 3): # "app/user/info"
        action = path.parts[2]
        controller = ".".join(path.parts[:2])

    controller_name = "controllers." + controller + "_controller"
    action_name = "_".join(action.split("-")) + "_action" 
    try:
        controller_module = importlib.import_module(controller_name)
    except ModuleNotFoundError:
        raise UserException("Page not found.", 404)
    
    if not hasattr(controller_module, action_name):
        raise UserException("Page not found.", 404)

    req.controller = controller_name
    req.action = action_name
    resp = getattr(controller_module, action_name)(req) #call action

    del_request_id()

    return resp

