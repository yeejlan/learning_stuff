import ope

def info_action(req):
    return ope.success("this is user/info page~")

def id_action(req):
    return ope.failed("id not found", ope.RESOURCE_NOT_FOUND)