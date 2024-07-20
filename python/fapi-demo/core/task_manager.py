from core import logger, request_context


class TaskManager:
    def __init__(self):
        self.error = None

    async def __aenter__(self):
        try:
            request_context.request_context_var.get()
        except Exception: #initial
            request_context.request_context_var.set({})

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            getLogger().error(f"Task failed: {exc_value}")
            self.error = exc_value
        else:
            pass
        
        return False


def getLogger():
    return logger.get_logger('task')