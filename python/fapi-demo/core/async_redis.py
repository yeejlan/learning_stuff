import json
import sys, os
from typing import Any

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from core import app

import redis.asyncio as redis_aio
import os

config = app.config

def create_pool(prefix :str = 'REDIS') -> redis_aio.ConnectionPool:
    host = config.get(f'{prefix}_URL', "redis://localhost:6379")
    pool = redis_aio.ConnectionPool.from_url(host)
    return pool


async def release_pool(pool: redis_aio.ConnectionPool):
    await pool.aclose()


class AsyncRedis:
    def __init__(self, pool: redis_aio.ConnectionPool, prefix: str = ''):
        self.pool = pool
        self.prefix = prefix

    async def get(self, key: str, default: str = '') -> str:
        async with redis_aio.Redis(connection_pool=self.pool) as client:
            value = await client.get(f'{self.prefix}{key}')
            return value.decode('utf-8') if value is not None else default

    async def getInt(self, key: str, default: int = 0) -> int:
        value = await self.get(key)
        try:
            return int(value)
        except ValueError:
            return default

    async def getDict(self, key: str, default: dict = {}) -> dict:
        value = await self.get(key)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default

    async def set(self, key: str, value: Any, ex = None) -> None:
        async with redis_aio.Redis(connection_pool=self.pool) as client:
            if isinstance(value, dict):
                value = json.dumps(value)
            await client.set(f'{self.prefix}{key}', value, ex)

    async def delete(self, key: str) -> None:
        async with redis_aio.Redis(connection_pool=self.pool) as client:
            await client.delete(f'{self.prefix}{key}')

    async def mget(self, keys: list[str], default: list[Any] = []) -> list[Any]:
        prefixed_keys = [f"{self.prefix}{key}" for key in keys]
        async with redis_aio.Redis(connection_pool=self.pool) as client:
            value = await client.mget(prefixed_keys)
            return value
        
    async def mset(self, key_values: dict[str, Any], ex = None) -> None:
        prefixed_key_values = {f"{self.prefix}{key}": value for key, value in key_values.items()}
        async with redis_aio.Redis(connection_pool=self.pool) as client:
            pipeline = client.pipeline()
            for key, value in prefixed_key_values.items():
                if isinstance(value, dict):
                    value = json.dumps(value)
                pipeline.set(key, value, ex)
            await pipeline.execute()


if __name__ == "__main__":
    import asyncio

    async def my_opeartion():
        pool = create_pool()
        print(pool)
        aredis = AsyncRedis(pool, 'MY_')
        await aredis.set('abc', 12345, 3600)
        await aredis.set('def', 67890, 3600)
        res1 = await aredis.get('def')
        await aredis.delete('def')
        res2 = await aredis.get('abc')
        res3 = await aredis.get('def')
        print([res1, res2, res3])

        key_values = {f"key{i}": f"value{i}" for i in range(1, 6)}
        await aredis.mset(key_values, 3600)
        keys = [f"key{i}" for i in range(1, 6)]
        res4 = await aredis.mget(keys)
        print(res4)

        await release_pool(pool)


    asyncio.run(my_opeartion())