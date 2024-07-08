import json
import sys, os
from typing import Any

sys.path.append(os.getcwd())
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
    def __init__(self, pool: redis_aio.ConnectionPool):
        self.pool = pool

    async def get(self, key: str, default: str = '') -> str:
        async with redis_aio.Redis(connection_pool=self.pool) as client:
            value = await client.get(key)
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

    async def set(self, key: str, value: Any) -> None:
        async with redis_aio.Redis(connection_pool=self.pool) as client:
            if isinstance(value, dict):
                value = json.dumps(value)
            await client.set(key, value)

    async def delete(self, key: str) -> None:
        async with redis_aio.Redis(connection_pool=self.pool) as client:
            await client.delete(key)


if __name__ == "__main__":
    import asyncio

    async def my_opeartion():        
        pool = create_pool()
        aredis = AsyncRedis(pool)
        await aredis.set('abc', 12345)
        await aredis.set('def', 67890)
        res1 = await aredis.get('def')
        await aredis.delete('def')
        res2 = await aredis.get('abc')
        res3 = await aredis.get('def')
        print([res1, res2, res3])

        await release_pool(pool)


    asyncio.run(my_opeartion())