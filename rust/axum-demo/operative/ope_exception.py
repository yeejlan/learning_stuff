class UserException(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.message = message
        self.code = code

class ModelException(Exception):
    pass

class ServiceException(Exception):
    pass

class FluxException(Exception):
    pass