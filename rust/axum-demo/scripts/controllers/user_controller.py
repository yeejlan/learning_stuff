import spy
import ope

def info_action(req: spy.SpyRequest) -> spy.SpyResponse:
    return ope.success("this is user/info page~")

