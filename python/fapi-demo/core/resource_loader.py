import sys, os
sys.path.append(os.getcwd())
import aiomysql
from typing import Dict, Any
from core import db_mysql

class ResourceLoaderException(Exception):
    pass

class ResourceLoader:
    def __init__(self):
        self.mysql_resources: Dict[str, Any] = {}

    async def createMysqlPool(self, prefix = "DB"):
        if prefix not in self.mysql_resources:
            self.mysql_resources[prefix] = await db_mysql.create_pool(prefix)
        return self.mysql_resources[prefix]

    def getMysqlPool(self, prefix = "DB") -> aiomysql.Pool:
        pool = self.mysql_resources.get(prefix)
        if not pool:
            raise ResourceLoaderException(f"mysql pool not found: {pool}")
        return pool

    async def closeMysqlPool(self, prefix = "DB"):
        if prefix in self.mysql_resources:
            self.mysql_resources[prefix].close()
            await self.mysql_resources[prefix].wait_closed()
            del self.mysql_resources[prefix]


    async def loadAll(self):
        await self.createMysqlPool('DB')

    async def closeAll(self):
        await self.closeMysqlPool('DB')



resource_loader = ResourceLoader()

def getResourceLoader() -> ResourceLoader:
    return resource_loader



if __name__ == "__main__":
    import asyncio

    async def printMysqlVersion():        
        resourceLoader = getResourceLoader()
        await resourceLoader.loadAll()
        print(resource_loader.mysql_resources)

        pool = resourceLoader.getMysqlPool('DB');
        res = await db_mysql.select("select version()", (), pool)
        print(res)

        await resourceLoader.closeAll()
        print(resource_loader.mysql_resources)

    asyncio.run(printMysqlVersion())