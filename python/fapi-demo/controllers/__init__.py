from fastapi import APIRouter
from . import user_controller
from . import test_controller, home_controller


router = APIRouter()

router.include_router(home_controller.router, prefix="/home", tags=["home"])
router.include_router(user_controller.router, prefix="/user", tags=["user"])
router.include_router(test_controller.router, prefix="/test", tags=["test"])

