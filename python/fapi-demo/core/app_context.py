from enum import IntEnum
import sys, os
sys.path.append(os.getcwd())
from core.config import Config
from typing import Dict, Any

class AppException(Exception):
    pass

class Environment(IntEnum):
    PRODUCTION = 10
    STAGING = 20
    TESTING = 30
    DEVELOPMENT = 40

class AppContext:
    _instance = None
    _setting: Dict[str, Any] = {}
    _is_init: bool = False
    _config: Config
    _is_debug: bool = False

    @classmethod
    def init(cls, config_file: str) -> None:
        if not cls._instance:
            cls._instance = cls()
        
        cls._config = Config(config_file)
        env_string = cls._config.get('APP_ENV', 'production');
        env = getattr(Environment, env_string.upper())
        cls._setting['env_string'] = env_string
        cls._setting['env'] = env
        
        is_debug = cls._config.getBool('APP_DEBUG', False);
        if env == Environment.PRODUCTION:
            is_debug = False
        cls._setting['debug'] = is_debug
        cls._is_debug = is_debug
        cls._is_init = True

    @classmethod
    def get_env(cls) -> Environment:
        cls._check_init()
        return cls._setting['env']

    @classmethod
    def get_env_string(cls) -> str:
        cls._check_init()
        return cls._setting['env_string']

    @classmethod
    def get_config(cls) -> Config:
        cls._check_init()
        return cls._config

    @classmethod
    def get_setting(cls) -> Dict[str, Any]:
        cls._check_init()
        return cls._setting
    
    @classmethod
    def is_debug_mode(cls) -> bool:
        if not cls._is_debug:
            return False
        return True

    @classmethod
    def _check_init(cls) -> None:
        if not cls._is_init:
            raise AppException(f'Please call {cls.__name__}.init first')
        
if __name__ == "__main__":
    AppContext.init('.env')

    env = AppContext.get_env()
    env_string = AppContext.get_env_string()

    print((env, env_string))

    config = AppContext.get_config()
    db_host = config.get('DB_HOST', 'localhost')
    print(db_host)

    settings = AppContext.get_setting()
    is_debug = AppContext.is_debug_mode()
    print(settings, is_debug)