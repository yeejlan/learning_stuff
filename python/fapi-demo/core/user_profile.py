from collections import UserDict
from typing import Optional
from core.auth_context import getUserId
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

#depends
async def launch_user_profile():
    profile = UserProfile()

    await profile.load() #load profile

    yield profile

    await profile.save() #save profile


class UserProfile(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._changed = False
        self._uid = 0

    def touch(self) -> None:
        self._changed = True

    def has_changed(self) -> bool:
        return self._changed

    def __setitem__(self, key, value):
        self._changed = True
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self._changed = True
        super().__delitem__(key)

    async def load(self, user_id: Optional[int] = None):
        if not user_id:
            user_id = getUserId()
        if user_id < 1:
            return

        self.data = await storage_manager.aredis.get(str(user_id), {})
        self._uid = user_id
        return self.data

    async def save(self):
        if self._uid and self.has_changed():
            await storage_manager.aredis.set(str(self._uid), self.data, PROFILE_LIFETIME)

    def get_user_id(self) -> int:
        return self._uid


if __name__ == "__main__":
    import asyncio
    from core import resource_loader

    async def main():
        loader = resource_loader.getResourceLoader()
        await loader.loadAll()

        uid = 13586
        user_profile = UserProfile()
        await user_profile.load(uid)
        count = user_profile.get('count', 0)
        user_profile['count'] = count + 1
        user_profile['device'] = 'ios'
        await user_profile.save()
        print(user_profile.data)

        await loader.releaseAll()

    asyncio.run(main())