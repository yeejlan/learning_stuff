
class UserException(Exception):
    def __init__(self, message: str, code: int = 1000):
        self.code = code
        self.message = message

class ServiceException(Exception):
    pass

class ModelException(Exception):
    pass

class FluxException(Exception):
    pass