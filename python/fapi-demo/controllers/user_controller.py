from fastapi import APIRouter
from reply import Reply

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