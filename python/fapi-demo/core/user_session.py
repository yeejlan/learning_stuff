import sys, os
working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

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

class SessionManager:
    def __init__(self):
        self._aredis = None

    @property
    def aredis(self):
        if self._aredis is None:
            loader = resource_loader.getResourceLoader()
            self._aredis = async_redis.AsyncRedis(loader.getRedisPool("REDIS"), 'SID_')
        return self._aredis

session_manager = SessionManager()

class UserSession:
    _var = ContextVar("session_data", default={})

    @classmethod
    def get(cls, key: str, default: str = '') -> str:
        return cls._var.get().get(key, default)
    
    @classmethod
    def getInt(cls, key: str, default: int = 0) -> int:
        value = cls.get(key)
        try:
            return int(value)
        except ValueError:
            return default
        
    @classmethod
    def delete(cls, key: str, value: Any) -> None:
        data = cls._var.get()
        del data[key]
        cls._var.set(data)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        data = cls._var.get()
        data[key] = value
        cls._var.set(data)

    @classmethod
    def setDict(cls, data: Dict = {}) -> None:
        session_data = cls._var.get()
        for key in data:
            session_data[key] = data[key]
        cls._var.set(session_data)

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        return cls._var.get()
    
    @classmethod
    async def load(cls, sid: str):
        data = await session_manager.aredis.getDict(sid, {})
        cls._var.set(data)
        return data

    @classmethod
    async def save(cls, sid: str):
        data = cls._var.get()
        await session_manager.aredis.set(sid, data, SESSION_LIFETIME)
    
    @classmethod
    def newSessionId(cls) -> str:
        return str(uuid4())
    
    @classmethod
    async def renew(cls, sid) -> str:
        await cls.destroy(sid)
        return cls.newSessionId()

    @classmethod
    async def destroy(cls, sid):
        cls._var.set({})
        await session_manager.aredis.set(sid, {})
    
    @classmethod
    def touch(cls):
        current_time = time.time()
        cls.set(SESSION_REFRESH_KEY, current_time)

    @classmethod
    def getSessionId(cls, req: Request):
        sid = req.cookies.get(SESSION_NAME)
        return sid


class UserSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        refreshCookie = False
        sid = request.cookies.get(SESSION_NAME)
        if not sid:
            refreshCookie = True
            sid = UserSession.newSessionId()

        data = await UserSession.load(sid) #load session

        if data:
            last_update = data.get(SESSION_REFRESH_KEY)
            current_time = time.time()
            if not last_update or (current_time - last_update) > SESSION_REFRESH_INTERVAL:
                UserSession.set(SESSION_REFRESH_KEY, current_time)
                refreshCookie = True

        response = await call_next(request)
        #save session
        await UserSession.save(sid)

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
        data = await UserSession.load(sid) #load session
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