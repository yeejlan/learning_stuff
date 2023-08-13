from typing import Generator
from fastapi import APIRouter, Depends
from reply import Reply

router = APIRouter()

@router.get("/")
def index():
    return "this is test/index page"

@router.get("/info")
def info():
    return Reply.failed("failed to get test.info", Reply.OPERATION_NOT_ALLOWED)


def get_db_pool() -> Generator:
    try:
        db = 'my db pool'
        print('db resource is created')
        yield db
    finally:
        print('db resource is closed')
        
def use_db_in_my_own_func(db=Depends(get_db_pool)):

    print("got db in my own func " + str(db))

@router.get("/auto-close")
def auto_close(db=Depends(get_db_pool)):
    use_db_in_my_own_func()
    return "got db:" + str(db) + ", and db pool should close automatically"

