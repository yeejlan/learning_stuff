from fastapi import APIRouter
from pydantic import BaseModel
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

@router.get("/find/{user_id:path}")
async def get_user_by_id(user_id: int):
    row = await user.get_user_by_id(user_id)
    if row:
        del row.password
    return Reply.success(row)

@router.get("/all")
async def get_all_users():
    rows = await user.list_users()
    if rows:
        for row in rows:
            del row.password
    return Reply.success(rows)
