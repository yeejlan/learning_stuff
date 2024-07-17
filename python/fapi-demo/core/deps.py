from core.exception import UserException
from core import auth_context
from core.config import getConfig
from fastapi import Depends, HTTPException

from core.user_session import launch_user_session

config = getConfig()
is_debug = config.getBool('APP_DEBUG', False)

async def ensure_debug_enabled():
    if not is_debug:
        raise HTTPException(status_code=401, detail="no access")


async def authorized_user_id() -> int:
    user_id = auth_context.getUserId()
    if user_id < 1:
        raise UserException('not authorized', 401)

    return user_id


ensureDebugEnabled = Depends(ensure_debug_enabled)
authorizedUserId = Depends(authorized_user_id)
launchUserSession = Depends(launch_user_session)

