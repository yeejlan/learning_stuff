
import spy
import ope

def err500_action(req: spy.SpyRequest) -> spy.SpyResponse:
    raise ope.ServiceException("my service is down!")

def user_error_action(req: spy.SpyRequest) -> spy.SpyResponse:
    raise ope.UserException("messsage from user_error_action", ope.OPERATION_FAILED)