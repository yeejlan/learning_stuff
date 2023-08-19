from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from contextvars import ContextVar


request_id = ContextVar('request_id', default='0000')  
channel = ContextVar('channel', default='app')

CUSTOM_FORMAT = '%(iso8601)s [%(channel)s] [%(levelname)s] %(message)s {request_id=%(request_id)s}'

class CustomLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name) 
        formatter = logging.Formatter(CUSTOM_FORMAT)
        handler = logging.StreamHandler() 
        handler.setFormatter(formatter)
        self.addHandler(handler)
        #add file handler
        file_handler = TimedRotatingFileHandler('storage/logs/uvicorn.log', when='midnight', delay=True)
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        if extra is None:
            extra = {
                'request_id': request_id.get(),
                'channel': channel.get(),
                'iso8601': datetime.utcnow().isoformat(),
            }
        super(CustomLogger, self)._log(level, msg, args, exc_info, extra)

logging.setLoggerClass(CustomLogger)

__logger= logging.getLogger('app.logger')

def get_logger(channel_name: str = 'app') -> logging.Logger:
    channel.set(channel_name)
    return __logger
