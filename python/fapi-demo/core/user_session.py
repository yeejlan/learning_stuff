import sys, os

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from core.config import getConfig
from core.uuid_helper import uuid_to_base58
import time
from fastapi import Request
from core import async_redis, resource_loader
from contextvars import ContextVar
from typing import Any, Dict
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4

SESSION_LIFETIME = 86400
SESSION_REFRESH_INTERVAL = 300
SESSION_REFRESH_KEY = "_last_update"
SESSION_NAME = "SESSIONID"

session_context: ContextVar[dict] = ContextVar("session_context")
session_id: ContextVar[str] = ContextVar("session_id")
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

class UserSession:

    @classmethod
    def get(cls, key: str, default: str = '') -> str:
        return session_context.get().get(key, default)
    
    @classmethod
    def getInt(cls, key: str, default: int = 0) -> int:
        value = cls.get(key)
        try:
            return int(value)
        except ValueError:
            return default
        
    @classmethod
    def delete(cls, key: str) -> None:
        data = session_context.get()
        del data[key]
        session_context.set(data)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        data = session_context.get()
        data[key] = value
        data['_changed'] = True
        session_context.set(data)

    @classmethod
    def setDict(cls, session_data: Dict = {}) -> None:
        data = session_context.get()
        for key in session_data:
            data[key] = session_data[key]
        data['_changed'] = True
        session_context.set(data)

    @classmethod
    def touch(cls) -> None:
        data = session_context.get()
        data['_changed'] = True
        session_context.set(data)

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        return session_context.get()
    
    @classmethod
    async def load(cls):
        data = await session_manager.aredis.getDict(session_id.get(), {})
        session_context.set(data)
        return data

    @classmethod
    async def save(cls, sid: str):
        data = session_context.get()
        await session_manager.aredis.set(sid, data, SESSION_LIFETIME)
    
    @classmethod
    def getSessionId(cls) -> str:
        return session_id.get()
    
    @classmethod
    def setSessionId(cls, sid: str):
        return session_id.set(sid)    

    @classmethod
    def newSessionId(cls) -> str:
        sid = uuid_to_base58(uuid4())
        session_id.set(sid)
        return sid
    
    @classmethod
    async def renew(cls, sid) -> str:
        await cls.destroy(sid)
        return cls.newSessionId()

    @classmethod
    async def destroy(cls, sid):
        session_context.set({})
        await session_manager.aredis.set(sid, {})


class UserSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        refreshCookie = False
        sid = request.cookies.get(SESSION_NAME)
        if sid:
            session_id.set(sid)
        else:
            refreshCookie = True
            sid = UserSession.newSessionId()
        token_sid = session_id.set(sid)
        token = session_context.set({})
        await UserSession.load() #load session


        response = await call_next(request)


        #save session
        data = session_context.get()
        if data:
            last_update = data.get(SESSION_REFRESH_KEY, '0')
            current_time = time.time()
            if not last_update or (current_time - float(last_update)) > SESSION_REFRESH_INTERVAL:
                UserSession.set(SESSION_REFRESH_KEY, current_time)
                refreshCookie = True

            changed = data.get('_changed')
            if changed:
                UserSession.delete('_changed')
                await UserSession.save(sid)

        session_context.reset(token)
        session_id.reset(token_sid)

        if refreshCookie: #setcookie
            response.set_cookie(SESSION_NAME, sid, SESSION_LIFETIME, httponly=True)
        return response

if __name__ == "__main__":
    import asyncio
    from core import resource_loader

    async def my_opeartion():
        loader = resource_loader.getResourceLoader()
        await loader.loadAll()

        sid = '12345'
        UserSession.setSessionId(sid)
        data = await UserSession.load() #load session
        count = UserSession.getInt('count')
        print(data)
        UserSession.touch()
        UserSession.setDict({
            "count": count+1,
            "uid": 123,
        })
        print(UserSession.get_all())
        await UserSession.save(sid) #save session
        await loader.releaseAll()

    asyncio.run(my_opeartion())