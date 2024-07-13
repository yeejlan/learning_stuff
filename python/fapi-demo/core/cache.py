from contextvars import ContextVar
import functools
import inspect
import json
import re
import sys, os

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)


from typing import Any, Callable, Coroutine, Dict, List, Optional, TypeVar, Union
from core.config import getConfig
from core import async_redis, resource_loader
from starlette.middleware.base import BaseHTTPMiddleware

CACHE_LIFETIME = 3600

cache_enabled: ContextVar[bool] = ContextVar("cache_enabled", default=True)

#middleware
class CacheRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        cache_refresh = request.query_params.get('cache_refresh', None)
        h_cache_refresh = request.headers.get('cache_refresh', None)
        if cache_refresh or h_cache_refresh:
            cache_enabled.set(False)

        response = await call_next(request)
        return response

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
        await cache_manager.aredis.set(key, value, ex)
    
    @classmethod
    async def mget(cls, keys: List[str]) -> List[Any]:
        return await cache_manager.aredis.mget(keys)
    
    @classmethod
    async def mgetDict(cls, keys: List[str]) -> List[Optional[Dict[str, Any]]]:
        byte_values = await cls.mget(keys)
        result_list = []
        for byte_value in byte_values:
            if byte_value is None:
                value = None
            else:
                try:
                    value = json.loads(byte_value)
                except json.JSONDecodeError:
                    value = None

            result_list.append(value)
        
        return result_list


    @classmethod
    async def mset(cls, key_values: dict[str, Any], ex: int = CACHE_LIFETIME) -> None:
        await cache_manager.aredis.mset(key_values, ex=ex)    

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

    @classmethod
    def cache_batch_result(cls, key: str, id_field: str = 'id', ex: int = CACHE_LIFETIME):
        def decorator(func: Callable[..., Coroutine[Any, Any, List[T]]]) -> Callable[..., Coroutine[Any, Any, List[T]]]:
            match = re.match(r'^([a-zA-Z]+)_\{([a-zA-Z_]+)\}$', key)
            if not match:
                raise ValueError("Key must be in the format 'prefix_{variable}', e.g., 'getUserInfo_{user_id}'")

            key_prefix, variable = match.groups()
        
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> List[T]:
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Check if the function has only one parameter and it's a list
                if len(bound_args.arguments) != 1 or not isinstance(next(iter(bound_args.arguments.values())), list):
                    raise ValueError("Function must have exactly one parameter of type list")

                # Get the list of ids
                ids = next(iter(bound_args.arguments.values()))
                
                # Check return type annotation
                return_type = sig.return_annotation
                if not (hasattr(return_type, '__origin__') and return_type.__origin__ is list):
                    raise ValueError("Function must return a list")
                
                item_type = return_type.__args__[0]
                if not (inspect.isclass(item_type) and (issubclass(item_type, dict) or hasattr(item_type, '__dict__'))):
                    raise ValueError("Function must return a list of dictionaries or objects with __dict__ attribute")

                # Build cache keys
                cache_keys = [f"{key_prefix}_{id}" for id in ids]

                # Retrieve data from cache
                cached_data = await cls.mgetDict(cache_keys)

                # Find ids missing from cache
                missing_ids = [id for id, data in zip(ids, cached_data) if data is None]

                # If there's missing data, call the original function
                if missing_ids:
                    missing_data = await func(missing_ids)
                    
                    # Ensure missing_data is a list of Dict or XxxModel
                    if not isinstance(missing_data, list) or not missing_data or not hasattr(missing_data[0], id_field):
                        raise ValueError(f"Function must return a list of objects with '{id_field}' attribute")

                    # Prepare data for caching
                    cache_update = {}
                    for item in missing_data:
                        item_id = getattr(item, id_field)
                        cache_update[f"{key_prefix}_{item_id}"] = item.__dict__ if hasattr(item, '__dict__') else item

                    # Update cache
                    await cls.mset(cache_update, ex)

                    # Update cached_data with new data
                    id_to_data = {getattr(item, id_field): item for item in missing_data}
                    for i, (id, data) in enumerate(zip(ids, cached_data)):
                        if data is None:
                            cached_data[i] = id_to_data[id].__dict__ if hasattr(id_to_data[id], '__dict__') else id_to_data[id] # type: ignore

                # Prepare final result
                result = []
                for data in cached_data:
                    if data is not None:
                        if issubclass(item_type, dict):
                            result.append(item_type(data))
                        else:
                            result.append(item_type(**data))

                return result

            return wrapper
        return decorator


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
        
        rows = await getUserByIds([105,12,13,14,15])
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