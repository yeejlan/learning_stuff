from collections import UserDict
from core.config import getConfig
from core.uuid_helper import uuid_to_base58
import time
from fastapi import Depends, Request, Response
from core import async_redis, resource_loader
from typing import Any, Dict
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4

SESSION_LIFETIME = 86400
SESSION_REFRESH_INTERVAL = 300
SESSION_REFRESH_KEY = "_last_update"
SESSION_NAME = "SESSIONID"

class SessionManager:
    def __init__(self):
        self._aredis = None
        config = getConfig()
        self._prefix = config.get('CACHE_PREFIX')

    @property
    def aredis(self):
        if self._aredis is None:
            loader = resource_loader.getResourceLoader()
            self._aredis = async_redis.AsyncRedis(loader.getRedisPool("REDIS"), f'{self._prefix}SID_')
        return self._aredis

session_manager = SessionManager()

class UserSession(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._changed = False
        self._sid = ''

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

    async def load(self, session_id: str):
        self.data = await session_manager.aredis.get(session_id, {})
        self._sid = session_id
        return self.data

    async def save(self):
        if self._sid and self.has_changed():
            await session_manager.aredis.set(self._sid, self.data, SESSION_LIFETIME)
    

    def get_session_id(self) -> str:
        return self._sid

    def set_session_id(self, session_id: str):
        self._sid = session_id

    def new_session_id(self) -> str:
        self._sid = uuid_to_base58(uuid4())
        self.touch()
        return self._sid
    
    async def renew(self, session_id: str) -> str:
        await self.destroy()
        return self.new_session_id()

    async def destroy(self):
        session_id = self.data['_sid']
        self.data = {}
        self._sid = ''
        await session_manager.aredis.set(session_id, {})



async def launch_user_session(request: Request, response: Response):
    session = UserSession()
    refresh_cookie = False
    sid = request.cookies.get(SESSION_NAME)
    if sid:
        session.set_session_id(sid)
    else:
        refresh_cookie = True
        sid = session.new_session_id()

    await session.load(sid) #load session

    last_update = session.get(SESSION_REFRESH_KEY, 0)
    current_time = time.time()
    if (current_time - float(last_update)) > SESSION_REFRESH_INTERVAL:
        session[SESSION_REFRESH_KEY] = current_time
        refresh_cookie = True    

    if refresh_cookie: #set cookie
        response.set_cookie(SESSION_NAME, sid, SESSION_LIFETIME, httponly=True)

    yield session

    await session.save() #save session


if __name__ == "__main__":
    import asyncio
    from core import resource_loader

    async def my_opeartion():
        loader = resource_loader.getResourceLoader()
        await loader.loadAll()

        sid = '12345'
        session = UserSession()
        data = await session.load(sid) #load session
        print(data)


        count = session.get('count', 0)
        session['count'] = count + 1
        session['uid'] = 123

        print(session)
        await session.save() #save session

        await loader.releaseAll()

    asyncio.run(my_opeartion())