from fastapi import APIRouter
from reply import Reply
from models import user

router = APIRouter()

@router.get("/")
def index():
    """
    user/index api.

    Output
 
    ```
    {
        "code": 0,
        "message": "success",
        "reason": "success",
        "data": "this is user/index page"
    }  
    ```
    """           
    return Reply.success("this is user/index page")

@router.get("/info")
def info():
    """
    user/info api.

    Output
 
    ```
    {
        "code": 0,
        "message": "success",
        "reason": "success",
        "data": "this is user/info page"
    }  
    ```
    """        
    return Reply.success("this is user/info page")

@router.get("/user")
async def get_user_by_id():
    row = await user.get_user_by_id(1)
    return Reply.success(repr(row))

