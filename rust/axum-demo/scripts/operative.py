import spy
import ope
import importlib
from pathlib import Path

def handle_request(req: spy.SpyRequest) -> spy.SpyResponse:
    return ope.pool.submit(_handle_request, req).result() 

def _handle_request(req: spy.SpyRequest) -> spy.SpyResponse:
    ope.set_request_id(req.request_id())

    #ope.info(req)
    # ope.info("handling~" + req.path)
    #raise ope.UserException("My test exception", 1234)
    # raise ope.ModelException("My model exception")

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
        raise ope.UserException("Page not found.", 404)
    
    if not hasattr(controller_module, action_name):
        raise ope.UserException("Page not found.", 404)

    resp = getattr(controller_module, action_name)(req) #call action

    ope.del_request_id

    return resp

