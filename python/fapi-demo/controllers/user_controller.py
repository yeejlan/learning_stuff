from fastapi import APIRouter
from reply import Reply

router = APIRouter()

@router.get("/")
def index():
    return Reply.success("this is user/index page")

@router.get("/info")
def info():
    return Reply.success("this is user/info page")