from enum import IntEnum
import sys, os
sys.path.append(os.getcwd())
from core.config import Config
from typing import Dict, Any, Optional

class AppException(Exception):
    pass

class Environment(IntEnum):
    PRODUCTION = 10
    STAGING = 20
    TESTING = 30
    DEVELOPMENT = 40

class AppContext:
    _instance: Optional['AppContext'] = None

    def __init__(self):
        self._setting: Dict[str, Any] = {}
        self._isInit: bool = False
        self._config: Optional[Config] = None
        self._isDebug: bool = False

    @classmethod
    def getInstance(cls) -> 'AppContext':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def init(cls, configFile: str) -> None:
        instance = cls.getInstance()
        instance._config = Config(configFile)
        envString = instance._config.get('APP_ENV', 'production')
        env = getattr(Environment, envString.upper())
        instance._setting['envString'] = envString
        instance._setting['env'] = env
        
        isDebug = instance._config.getBool('APP_DEBUG', False)
        if env == Environment.PRODUCTION:
            isDebug = False
        instance._setting['debug'] = isDebug
        instance._isDebug = isDebug
        instance._isInit = True

    @classmethod
    def getEnv(cls) -> Environment:
        instance = cls.getInstance()
        instance._checkInit()
        return instance._setting['env']

    @classmethod
    def getEnvString(cls) -> str:
        instance = cls.getInstance()
        instance._checkInit()
        return instance._setting['envString']

    @classmethod
    def getConfig(cls) -> Config:
        instance = cls.getInstance()
        instance._checkInit()
        return instance._config # type: ignore

    @classmethod
    def getSetting(cls) -> Dict[str, Any]:
        instance = cls.getInstance()
        instance._checkInit()
        return instance._setting.copy()  # Return a copy to prevent accidental modifications
    
    @classmethod
    def isDebugMode(cls) -> bool:
        instance = cls.getInstance()
        return instance._isDebug

    def _checkInit(self) -> None:
        if not self._isInit:
            raise AppException(f'Please call {self.__class__.__name__}.init first')

if __name__ == "__main__":
    AppContext.init('.env')

    env = AppContext.getEnv()
    envString = AppContext.getEnvString()

    print((env, envString))

    config = AppContext.getConfig()
    dbHost = config.get('DB_HOST', 'localhost')
    print(dbHost)

    settings = AppContext.getSetting()
    isDebug = AppContext.isDebugMode()
    print(settings, isDebug)