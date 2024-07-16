from typing import Any
from core.config import getConfig
from core import async_redis, resource_loader


PROFILE_LIFETIME = 86400*30   # 30 days

class StorageManager:
    def __init__(self):
        self._aredis = None
        config = getConfig()
        self._prefix = config.get('CACHE_PREFIX')

    @property
    def aredis(self):
        if self._aredis is None:
            loader = resource_loader.getResourceLoader()
            self._aredis = async_redis.AsyncRedis(loader.getRedisPool("REDIS"), f'{self._prefix}UID_')
        return self._aredis

storage_manager = StorageManager()

class UserProfileException(Exception):
    pass

class UserProfile:
    def __init__(self, user_id: str|int) -> None:
        self._profile :dict[str, Any] = {}
        self._user_id = str(user_id)

    async def _load(self) -> dict[str, Any]:
        data = await storage_manager.aredis.get(self._user_id, {})
        data['_loaded'] = True
        self._profile = data
        return data
    
    async def load(self) -> dict[str, Any]:
        if self._profile and '_loaded' in self._profile:
            return self._profile
        return await self._load()

    async def save(self):
        data = self._profile
        if data and '_changed' in data:
            del data['_changed']
            del data['_loaded']
        await storage_manager.aredis.set(self._user_id, data, PROFILE_LIFETIME)

    def get_user_id(self) -> str:
        return self._user_id
    
    def get_profile(self) -> dict[str, Any]: 
        return self._profile

    def set(self, key: str, value: Any) -> None:
        data = self._profile
        if not data or '_loaded' not in data:
            raise UserProfileException('Data not loaded, call load() first')
        data[key] = value
        data['_changed'] = True
        self._profile = data


if __name__ == "__main__":
    import asyncio
    from core import resource_loader

    async def main():
        loader = resource_loader.getResourceLoader()
        await loader.loadAll()

        uid = 13586
        user_profile = UserProfile(uid)
        await user_profile.load()
        user_profile.set('device', 'ios')
        print(user_profile.get_profile())
        await user_profile.save()
        print(user_profile.get_profile())

        await loader.releaseAll()

    asyncio.run(main())