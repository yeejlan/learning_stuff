import spy
import ope

def info_action(req: spy.SpyRequest) -> spy.SpyResponse:
    return ope.success("this is user/info page~")

def id_action(req: spy.SpyRequest) -> spy.SpyResponse:
    return ope.failed("id not found", 1400)