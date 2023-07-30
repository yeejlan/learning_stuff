class OpeException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

class UserException(OpeException):
    pass

class ModelException(OpeException):
    pass

class ServiceException(OpeException):
    pass

class FluxException(OpeException):
    pass