import sys, os

import redis.asyncio as redis_aio
sys.path.append(os.getcwd())
import aiomysql
from typing import Dict, Any
from core import async_redis, db_mysql

class ResourceLoaderException(Exception):
    pass

class ResourceLoader:
    def __init__(self):
        self.mysql_resources: Dict[str, Any] = {}
        self.redis_resources: Dict[str, Any] = {}

    async def createMysqlPool(self, prefix = "DB"):
        if prefix not in self.mysql_resources:
            self.mysql_resources[prefix] = await db_mysql.create_pool(prefix)
        return self.mysql_resources[prefix]

    def getMysqlPool(self, prefix = "DB") -> aiomysql.Pool:
        pool = self.mysql_resources.get(prefix)
        if not pool:
            raise ResourceLoaderException(f"mysql pool not found: {prefix}")
        return pool

    async def releaseMysqlPool(self, prefix = "DB"):
        if prefix in self.mysql_resources:
            self.mysql_resources[prefix].close()
            await self.mysql_resources[prefix].wait_closed()
            del self.mysql_resources[prefix]

    def createRedisPool(self, prefix = "REDIS") -> redis_aio.ConnectionPool:
        if prefix not in self.redis_resources:
            self.redis_resources[prefix] = async_redis.create_pool(prefix)
        return self.redis_resources[prefix]
        
    async def releaseRedisPool(self, prefix = "REDIS"):
        if prefix in self.redis_resources:
            await async_redis.release_pool(self.redis_resources[prefix])
            del self.redis_resources[prefix]

    def getRedisPool(self, prefix = "REDIS") -> redis_aio.ConnectionPool:
        pool = self.redis_resources.get(prefix)
        if not pool:
            raise ResourceLoaderException(f"redis pool not found: {prefix}")
        return pool             

    async def loadAll(self):
        await self.createMysqlPool('DB')
        self.createRedisPool('REDIS')

    async def releaseAll(self):
        await self.releaseMysqlPool('DB')
        await self.releaseRedisPool('REDIS')



resource_loader = ResourceLoader()

def getResourceLoader() -> ResourceLoader:
    return resource_loader



if __name__ == "__main__":
    import asyncio

    async def my_opeartion():
        resourceLoader = getResourceLoader()
        await resourceLoader.loadAll()
        print(resource_loader.mysql_resources)
        print(resource_loader.redis_resources)

        pool = resourceLoader.getMysqlPool('DB');
        res = await db_mysql.select("select version()", (), pool)
        print(res)

        aredis = async_redis.AsyncRedis(resource_loader.getRedisPool("REDIS"))
        await aredis.set('abc', '11335679')
        res = await aredis.get('abc')
        print(res)

        await resourceLoader.releaseAll()

    asyncio.run(my_opeartion())