from contextvars import ContextVar
import sys, os

from sympy import false

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)


from typing import Any
from core.config import getConfig
from core import async_redis, resource_loader

CACHE_LIFETIME = 3600

cache_enabled: ContextVar[bool] = ContextVar("cache_enabled", default=True)

class CacheManager:
    def __init__(self):
        self._aredis = None
        config = getConfig()
        self._prefix = config.get('CACHE_PREFIX')
        self._enabled = config.getBool('CACHE_ENABLED', True)

    def enabled(self) -> bool:
        if not self._enabled:
            return False
        if not cache_enabled.get():
            return False
        return True

    @property
    def aredis(self):
        if self._aredis is None:
            loader = resource_loader.getResourceLoader()
            self._aredis = async_redis.AsyncRedis(loader.getRedisPool("REDIS"), self._prefix)
        return self._aredis

cache_manager = CacheManager()
def getCacheManager() -> CacheManager:
    return cache_manager

class Cache:

    @classmethod
    async def get(cls, key: str, default: str = '') -> str:
        if not cache_manager.enabled():
            return default
        return await cache_manager.aredis.get(key, default)
    
    @classmethod
    async def getInt(cls, key: str, default: int = 0) -> int:
        if not cache_manager.enabled():
            return default        
        return await cache_manager.aredis.getInt(key, default)
    
    @classmethod
    async def getDict(cls, key: str, default: dict = {}) -> dict:
        return await cache_manager.aredis.getDict(key, default)  
        
    @classmethod
    async def delete(cls, key: str) -> None:
        return await cache_manager.aredis.delete(key)

    @classmethod
    async def set(cls, key: str, value: Any, ex: int = CACHE_LIFETIME) -> None:
        return await cache_manager.aredis.set(key, value, ex)

if __name__ == "__main__":
    import asyncio
    from core import resource_loader

    async def my_opeartion():
        loader = resource_loader.getResourceLoader()
        await loader.loadAll()

        key = 'cache_abc'
        await Cache.set(key, 12345)
        abc1 = await Cache.get(key)
        await Cache.delete(key)
        abc2 = await Cache.get(key)
        await Cache.set(key, 12345)
        print([abc1, abc2])
        
        await loader.releaseAll()

    asyncio.run(my_opeartion())