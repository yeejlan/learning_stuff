from fastapi.exceptions import RequestValidationError
from core import logger
from core.app import getApp
from core.auth_context import AuthContextAsgiMiddleware
from core.cache import RefreshCacheAsgiMiddleware
from core.request_context import RequestContextAsgiMiddleware
from core.exception import ExceptionHandlerAsgiMiddleware, validation_exception_handler
from starlette.middleware.cors import CORSMiddleware

app = getApp()

app.add_middleware(ExceptionHandlerAsgiMiddleware)
app.add_middleware(AuthContextAsgiMiddleware)
app.add_middleware(RequestContextAsgiMiddleware)
app.add_middleware(RefreshCacheAsgiMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", 
        "X-Requested-With", "Accept", "Origin",
        "Access-Control-Request-Headers", "Access-Control-Request-Method",
        "DNT", "X-CSRF-Token", "X-XSRF-TOKEN", "Cookie",
        "refresh-cache", "token", "lang",
    ],
)

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, ex):
    return validation_exception_handler(ex)

