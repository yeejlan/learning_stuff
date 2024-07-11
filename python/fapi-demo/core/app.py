import sys, os
working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from fastapi import FastAPI
from core.app_context import AppContext

AppContext.init()
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
