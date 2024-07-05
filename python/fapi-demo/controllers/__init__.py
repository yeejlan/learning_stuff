from fastapi import APIRouter
from . import home_controller
from . import user_controller,test_controller,wm_controller


router = APIRouter()

router.include_router(user_controller.router, prefix="/user", tags=["user"])
router.include_router(test_controller.router, prefix="/test", tags=["test"])
router.include_router(wm_controller.router, prefix="/wm", tags=["wm"])

