import sys, os
sys.path.append(os.getcwd())
from fastapi import FastAPI
from core.app_context import AppContext

AppContext.init('.env')
config = AppContext.getConfig()
isDebug = AppContext.isDebugMode()

appOptions = {
    "host": config.get('LISTEN_HOST', "0.0.0.0"),
    "port": config.getInt('LISTEN_PORT', 5000),
    "title": config.get('APP_NAME', "My FastApi Demo"),
    "version": config.get('APP_VERSION', "1.0.0"),
    "redoc_url": None  # disable ReDoc
}
if not isDebug:
    appOptions['docs_url'] = None

app = FastAPI(**appOptions)

def getApp() -> FastAPI:
    return app
