import spy
import ope

def handle_request(req):
    return ope.pool.submit(_handle_request, req).result() 

def _handle_request(req):
    print(req)