from contextvars import ContextVar
import sys, os

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from typing import Any, Callable, Coroutine, List, TypeVar
import functools
import inspect
import asyncio
import re

from core.config import getConfig
from core import async_redis, resource_loader
from starlette.requests import Request as StarRequest

CACHE_LIFETIME = 3600

cache_enabled: ContextVar[bool] = ContextVar("cache_enabled")

#middleware
class CacheRefreshAsgiMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        ctx = True
        request = StarRequest(scope)
        cache_refresh = request.query_params.get('cache_refresh', None)
        h_cache_refresh = request.headers.get('cache_refresh', None)
        if cache_refresh or h_cache_refresh:
            ctx = False

        token = cache_enabled.set(ctx)
        try:
            await self.app(scope, receive, send)
        finally:
            cache_enabled.reset(token)

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
    async def get(cls, key: str, default: Any = None) -> Any:
        if not cache_manager.enabled():
            return default
        return await cache_manager.aredis.get(key, default)

    @classmethod
    async def delete(cls, key: str) -> None:
        return await cache_manager.aredis.delete(key)

    @classmethod
    async def set(cls, key: str, value: Any, ex: int = CACHE_LIFETIME) -> None:
        await cache_manager.aredis.set(key, value, ex)
    
    @classmethod
    async def mget(cls, keys: List[str]) -> List[Any]:
        return await cache_manager.aredis.mget(keys)

    @classmethod
    async def mset(cls, key_values: dict[str, Any], ex: int = CACHE_LIFETIME) -> None:
        await cache_manager.aredis.mset(key_values, ex=ex)    

    @classmethod
    def memorize(cls, key: str, ex: int = CACHE_LIFETIME):
        def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                cache_key = key.format(**bound_args.arguments)

                cached_result = await cls.get(cache_key)
                if cached_result is not None:
                    return cached_result

                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = await cls.run_sync(func, *args, **kwargs)

                await cls.set(cache_key, result, ex)

                return result

            return wrapper
        return decorator

    @classmethod
    def forget(cls, key: str):
        def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                cache_key = key.format(**bound_args.arguments)

                if inspect.iscoroutinefunction(func):
                    res = await func(*args, **kwargs)
                else:
                    res = await cls.run_sync(func, *args, **kwargs)

                await cls.delete(cache_key)
                return res

            return wrapper
        return decorator

    @staticmethod
    async def run_sync(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    @classmethod
    def memorize_many(cls, key: str, id_field: str = 'id', ex: int = CACHE_LIFETIME):
        def decorator(func: Callable[..., Coroutine[Any, Any, List[T]]]) -> Callable[..., Coroutine[Any, Any, List[T]]]:
            match = re.match(r'^([a-zA-Z]+)_\{([a-zA-Z_]+)\}$', key)
            if not match:
                raise ValueError("Key must be in the format 'prefix_{variable}', e.g., 'getUserInfo_{user_id}'")

            key_prefix, variable = match.groups()
        
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> List[T]:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                if len(bound_args.arguments) != 1 or not isinstance(next(iter(bound_args.arguments.values())), list):
                    raise ValueError("Function must have exactly one parameter of type list")

                ids = next(iter(bound_args.arguments.values()))
                
                cache_keys = [f"{key_prefix}_{id}" for id in ids]

                cached_data = await cls.mget(cache_keys)

                missing_ids = [id for id, data in zip(ids, cached_data) if data is None]

                if missing_ids:
                    missing_data = await func(missing_ids)
                    
                    if not isinstance(missing_data, list) or not missing_data or not hasattr(missing_data[0], id_field):
                        raise ValueError(f"Function must return a list of objects with '{id_field}' attribute")

                    cache_update = {}
                    for item in missing_data:
                        item_id = getattr(item, id_field)
                        cache_update[f"{key_prefix}_{item_id}"] = item

                    await cls.mset(cache_update, ex)

                    id_to_data = {getattr(item, id_field): item for item in missing_data}
                    for i, (id, data) in enumerate(zip(ids, cached_data)):
                        if data is None:
                            cached_data[i] = id_to_data[id]

                return [data for data in cached_data if data is not None]

            return wrapper
        return decorator
    
if __name__ == "__main__":
    import asyncio
    from core import resource_loader

    async def my_opeartion():
        loader = resource_loader.getResourceLoader()
        await loader.loadAll()
        cache_enabled.set(True)

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
        
        rows = await getUserByIds([105,12,13,14,15,16])
        for row in rows:
            print(row)

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

    @Cache.cache_batch_result(key="getUserInfo_{user_id}")
    async def getUserByIds(ids: list[int]) ->list[UserModel]:
        # Simulate fetching user info
        rows = []
        for id in ids:
            rows.append(UserModel(id=id, name=f'User#{id}'))
        return rows

    asyncio.run(my_opeartion())    