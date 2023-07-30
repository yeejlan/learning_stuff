import spy
import ope

def handle_request(req: spy.SpyRequest):
    return ope.pool.submit(_handle_request, req).result() 

def _handle_request(req: spy.SpyRequest):
    ope.set_request_id(req.request_id())
    #ope.info(req)
    ope.info("handling~" + req.path)
    raise ope.UserException("cccc", 1234)
    ope.del_request_id