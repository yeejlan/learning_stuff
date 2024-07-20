from contextlib import asynccontextmanager
from typing import Optional

from pydantic import BaseModel

from fastapi import Depends, FastAPI, HTTPException, Query
from core.app_context import AppContext
from core.resource_loader import getResourceLoader
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

AppContext.init()
config = AppContext.getConfig()
openapi_enabled = config.getBool('OPENAPI_ENABLED', False)
is_debug = config.getBool('APP_DEBUG', False)

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
    "docs_url": None,  # disable docs
    "servers": servers,
}
if not openapi_enabled:
    appOptions['openapi_url'] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await getResourceLoader().loadAll()
    yield
    await getResourceLoader().releaseAll()


class DebugQueryParams(BaseModel):
    _user_id: Optional[int] = None
    _skip_auth: Optional[int] = None
    refresh_cache: Optional[int] = None

async def get_debug_query_params(
    _user_id: Optional[int] = Query(None),
    _skip_auth: Optional[int] = Query(None),
    refresh_cache: Optional[int] = Query(None)
) -> Optional[DebugQueryParams]:
    if not is_debug:
        return None
    return DebugQueryParams(
        _user_id=_user_id,
        _skip_auth=_skip_auth,
        refresh_cache=refresh_cache
    )

dependencies = []
if is_debug:
    dependencies = [Depends(get_debug_query_params)]

app = FastAPI(
    lifespan=lifespan, 
    dependencies=dependencies, 
    **appOptions
    )

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    if not is_debug:
        raise HTTPException(404)

    return get_swagger_ui_html(
        openapi_url=app.openapi_url, # type: ignore
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False) # type: ignore
async def swagger_ui_redirect():
    if not is_debug:
        raise HTTPException(404)

    return get_swagger_ui_oauth2_redirect_html()

 
def getApp() -> FastAPI:
    return app
