from datetime import datetime
import logging
from contextvars import ContextVar

request_id = ContextVar('request_id', default='0000')  
channel = ContextVar('channel', default='app')


FORMAT = '%(iso8601)s [%(channel)s] [%(levelname)s] %(message)s {request_id=%(request_id)s}'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


class CustomLogger(logging.Logger):

    def _log(self, level, msg, args, exc_info=None, extra=None):
        if extra is None:
            extra = {
                'request_id': request_id.get(),
                'channel': channel.get(),
                'iso8601': datetime.utcnow().isoformat(),
            }
        super(CustomLogger, self)._log(level, msg, args, exc_info, extra)

logging.setLoggerClass(CustomLogger)

__logger= logging.getLogger(__name__)

def get_logger(channel_name: str = 'app') -> logging.Logger:
    channel.set(channel_name)
    return __logger
