from contextvars import ContextVar
import functools
import inspect
import sys, os

from sympy import Union, false

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)


from typing import Any, Awaitable, Callable, Coroutine, TypeVar
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

T = TypeVar('T')
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

    @classmethod
    def cache_result(cls, key: str, ex: int = CACHE_LIFETIME):
        def decorator(func: Callable[..., T]) -> Callable[..., Coroutine[Any, Any, T]]:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Build cache key
                cache_key = key.format(**bound_args.arguments)

                # Get return type
                return_type = sig.return_annotation

                # Check cache
                cached_result = await cls.get_cached_result(cache_key, return_type)
                if cached_result is not None:
                    return cached_result

                # If no cache, call the original function
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = await cls.run_sync(func, *args, **kwargs)

                # Cache the result
                await cls.set_cache_result(cache_key, result, ex)

                return result

            return wrapper
        return decorator

    @classmethod
    def cache_delete(cls, key: str):
        def decorator(func: Callable[..., T]) -> Callable[..., Coroutine[Any, Any, T]]:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Build cache key
                cache_key = key.format(**bound_args.arguments)

                # Call the original function
                res = None
                if inspect.iscoroutinefunction(func):
                    res = await func(*args, **kwargs)
                else:
                    res = await cls.run_sync(func, *args, **kwargs)

                # Delete cache
                await cls.delete(cache_key)
                return res

            return wrapper
        return decorator

    @classmethod
    async def get_cached_result(cls, key: str, return_type: Any) -> Any:
        # Get cached result based on return type
        if return_type == str:
            return await cls.get(key)
        elif return_type == int:
            return await cls.getInt(key)
        else:
            cached_dict = await cls.getDict(key)
            return cls.dict_to_return_type(cached_dict, return_type) if cached_dict else None

    @classmethod
    async def set_cache_result(cls, key: str, value: Any, ex: int) -> None:
        # Set cache result
        if isinstance(value, (str, int)):
            await cls.set(key, value, ex)
        elif hasattr(value, '__dict__'):
            await cls.set(key, value.__dict__, ex)
        else:
            await cls.set(key, value, ex)

    @staticmethod
    def dict_to_return_type(data: dict, return_type: Any) -> Any:
        if data is None:
            return None
        if inspect.isclass(return_type) and issubclass(return_type, dict):
            return return_type(data)
        elif hasattr(return_type, '__annotations__'):
            return return_type(**data)
        else:
            return data

    @staticmethod
    async def run_sync(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        # Execute synchronous function in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


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

        user = await get_user_info(101, 'Yaoshui Yan')
        print(user)
        #await update_user_info(101, "user is deleted from cache!")
        
        await loader.releaseAll()


    class UserModel:
        def __init__(self, id: int, name: str):
            self.id = id
            self.name = name

        def __str__(self):
            return f"UserModel(id={self.id}, name='{self.name}')"            

    @Cache.cache_result(key="getUserInfo_{user_id}")
    async def get_user_info(user_id: int, name: str) -> UserModel:
        # Simulate fetching user info
        return UserModel(id=user_id, name=name)

    @Cache.cache_delete(key="getUserInfo_{user_id}")
    async def update_user_info(user_id: int, new_name: str) -> None:
        # Update user info logic
        pass

    asyncio.run(my_opeartion())