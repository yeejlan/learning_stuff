import spy
import ope

def handle_request(req: spy.SpyRequest) -> spy.SpyResponse:
    return ope.pool.submit(_handle_request, req).result() 

def _handle_request(req: spy.SpyRequest) -> spy.SpyResponse:
    ope.set_request_id(req.request_id())

    #ope.info(req)
    # ope.info("handling~" + req.path)
    raise ope.UserException("My test exception", 1234)
    
    resp = spy.SpyResponse()
    resp.status_code = 200
    resp.content = "handle " + req.path + " finished"

    ope.del_request_id

    return resp

    