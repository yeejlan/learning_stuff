import sys, os
working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from fastapi import FastAPI
from core.app_context import AppContext

AppContext.init()
config = AppContext.getConfig()
isDebug = AppContext.isDebugMode()

servers=[
            {"url": "/", "description": "Local"},
            {"url": "https://stag.example.com", "description": "Staging environment"},
            {"url": "https://prod.example.com", "description": "Production environment"},
];

appOptions = {
    "host": config.get('LISTEN_HOST', "0.0.0.0"),
    "port": config.getInt('LISTEN_PORT', 5000),
    "title": config.get('APP_NAME', "My FastApi Demo"),
    "version": config.get('APP_VERSION', "1.0.0"),
    "redoc_url": None,  # disable ReDoc
    "servers": servers,
}
if not isDebug:
    appOptions['docs_url'] = None

app = FastAPI(**appOptions)

def getApp() -> FastAPI:
    return app
