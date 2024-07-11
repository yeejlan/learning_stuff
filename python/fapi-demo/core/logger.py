import sys, os
working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

import logging
from contextvars import ContextVar
from core.request_context import getRequestContextDict
from core.util import now_as_iso8601, now_with_timezone

channel = ContextVar('channel', default='app')

CUSTOM_FORMAT = '%(iso8601)s [%(channel)s] [%(levelname)s] %(message)s %(context)s'

def getDailyLogName(channel:str = 'app', path:str = 'storage/logs'):
    today = now_with_timezone()
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
        log_file = getDailyLogName(channel = name)
        file_handler = logging.FileHandler(log_file, delay=True)
        file_handler.setFormatter(custom_formatter)
        self.addHandler(file_handler)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        if extra is None:
            request_context = getRequestContextDict()
            context = {}
            for key, value in request_context.items():
                if not key.startswith("_"):
                    context[key] = value
         
            extra = {
                'channel': channel.get(),
                'iso8601': now_as_iso8601(),
                'context': context,
            }

        super(CustomLogger, self)._log(level, msg, args, exc_info, extra)

logger_dict: dict[str, logging.Logger] = {}


def makeCustomeLogger(channel = 'app'):
    logger_name = channel
    logger= logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    return logger

def buildInitialLoggers(logger_channels: list[str] = ['app', 'err500']):
    old_logger_clazz = logging.getLoggerClass()
    logging.setLoggerClass(CustomLogger)

    for channel in logger_channels:
        logger_dict[channel] = makeCustomeLogger(channel)

    logging.setLoggerClass(old_logger_clazz)

def getLogger(channel_name: str = 'app') -> logging.Logger:
    return get_logger(channel_name)

def get_logger(channel_name: str = 'app') -> logging.Logger:
    channel.set(channel_name)
    if channel_name in logger_dict:
        return logger_dict[channel_name]
    
    return logger_dict['app']


if __name__ == "__main__":
    buildInitialLoggers(['app', 'err500'])
    log_name = getDailyLogName('mylog', 'my/log/storage/path')
    print(log_name)

