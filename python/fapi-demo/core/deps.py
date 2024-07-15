import sys, os

from core.exception import UserException

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from core import auth
from core.config import getConfig
from fastapi import Depends, HTTPException

config = getConfig()
is_debug = config.getBool('APP_DEBUG', False)

async def ensure_debug_enabled():
    if not is_debug:
        raise HTTPException(status_code=401, detail="no access")

ensureDebugEnabled = Depends(ensure_debug_enabled)

async def ensure_user_loggedin() -> int:
    uid = auth.getLoggedinUserId()
    user_id = int(uid) if uid else 0
    if user_id < 1:
        raise UserException('not authorized', 401)

    return user_id

ensureUserLoggedin = Depends(ensure_user_loggedin)