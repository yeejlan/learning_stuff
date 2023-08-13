from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def index():
    return "this is homepage"

@router.get("/info")
def info():
    return "this is home/info page"