import logging

from core.request_context import getRequestContext
from core.time_util import now_as_datetime, now_as_iso8601

CUSTOM_FORMAT = '%(iso8601)s [%(channel)s] [%(levelname)s] %(message)s %(context)s'

def getDailyLogName(channel:str = 'app', path:str = 'storage/logs'):
    today = now_as_datetime()
    today_str = today.strftime("%Y-%m-%d")
    return f'{path}/{channel}-{today_str}.log'

class CustomLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        custom_formatter = logging.Formatter(CUSTOM_FORMAT)

        # add stdout
        handler = logging.StreamHandler() 
        handler.setFormatter(custom_formatter)
        self.addHandler(handler)

        # add file handler
        file_handler = makeFilehandler(name)
        self.addHandler(file_handler)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        if extra is None:
            context = {}
            try:
                request_context = getRequestContext()
                for key, value in request_context.items():
                    if not key.startswith("_"):
                        context[key] = value                
            except Exception:
                pass
         
            extra = {
                'channel': self.name,
                'iso8601': now_as_iso8601(),
                'context': context,
            }

        super(CustomLogger, self)._log(level, msg, args, exc_info, extra)

logger_channels = ['app', 'err500']
logger_dict: dict[str, logging.Logger] = {}
logger_file_handler_dict: dict[str, logging.FileHandler] = {}

def makeCustomeLogger(name = 'app'):
    logger= CustomLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

def makeFilehandler(name = 'app'):
    if name not in logger_channels:
        name = 'app'

    if name not in logger_file_handler_dict:
        log_file = getDailyLogName(channel = name)
        file_handler = logging.FileHandler(log_file, delay=True)
        custom_formatter = logging.Formatter(CUSTOM_FORMAT)
        file_handler.setFormatter(custom_formatter)
        logger_file_handler_dict[name] = file_handler

    return logger_file_handler_dict[name]


def getLogger(channel_name: str = 'app') -> logging.Logger:
    return get_logger(channel_name)

def get_logger(channel_name: str = 'app') -> logging.Logger:
    if channel_name not in logger_dict:
        logger_dict[channel_name] = makeCustomeLogger(channel_name)
    
    return logger_dict[channel_name]



if __name__ == "__main__":
    log_name = getDailyLogName('mylog', 'my/log/storage/path')
    print(log_name)

    logger_app = getLogger('app')
    logger_err500 = getLogger('err500')
    logger_colamode = getLogger('colamode')
    logger_app.info('This is a test log message from logger_app.')
    logger_err500.info('This is a test log message from logger_err500.')
    logger_colamode.info('This is a test log message from logger_colamode.')

    print()
    print(logger_dict)
    print()
    print(logger_file_handler_dict)
