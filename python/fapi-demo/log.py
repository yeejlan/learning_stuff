from datetime import datetime
import logging
from contextvars import ContextVar
from core.util import now_as_iso8601, now_with_timezone

request_id = ContextVar('request_id', default='0000')
uid = ContextVar('uid', default=0)
channel = ContextVar('channel', default='app')

CUSTOM_FORMAT = '%(iso8601)s [%(channel)s] [%(levelname)s] %(message)s {uid=%(uid)s, request_id=%(request_id)s}'

def get_daily_log_name(channel:str = 'app', path:str = 'storage/logs'):
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
        log_file = get_daily_log_name(channel = name)
        file_handler = logging.FileHandler(log_file, delay=True)
        file_handler.setFormatter(custom_formatter)
        self.addHandler(file_handler)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        if extra is None:
            extra = {
                'request_id': request_id.get(),
                'uid': uid.get(),
                'channel': channel.get(),
                'iso8601': now_as_iso8601(),
            }
        super(CustomLogger, self)._log(level, msg, args, exc_info, extra)

logger_dict: dict[str, logging.Logger] = {}


def make_custome_logger(channel = 'app'):
    logger_name = channel
    logger= logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)    
    return logger

def build_initial_loggers(logger_channels: list[str] = ['app', 'err500']):
    old_logger_clazz = logging.getLoggerClass()
    logging.setLoggerClass(CustomLogger)

    for channel in logger_channels:
        logger_dict[channel] = make_custome_logger(channel)

    logging.setLoggerClass(old_logger_clazz)

def get_logger(channel_name: str = 'app') -> logging.Logger:
    channel.set(channel_name)
    if channel_name in logger_dict:
        return logger_dict[channel_name]
    
    return logger_dict['app']

build_initial_loggers(['app', 'err500'])


if __name__ == "__main__":
    log_name = get_daily_log_name('mylog', 'my/log/storage/path')
    print(log_name)

