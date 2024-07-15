import sys, os

working_path = os.getcwd()
if working_path not in sys.path:
    sys.path.append(working_path)

from core.config import getConfig
from fastapi import Depends, HTTPException

config = getConfig()
is_debug = config.getBool('APP_DEBUG', False)

async def ensure_debug_enabled():
    if not is_debug:
        raise HTTPException(status_code=401, detail="no access")

ensureDebugEnabled = Depends(ensure_debug_enabled)
