from fastapi import APIRouter
from reply import Reply

router = APIRouter()

@router.get("/")
def index():
    """
    home api.

    Output
 
    ```
    {
        "code": 0,
        "message": "success",
        "reason": "success",
        "data": "this is homepage"
    }  
    ```
    """      
    return Reply.success("this is homepage")

@router.get("/info")
def info():
    """
    home/info api.

    Output
 
    ```
    {
        "code": 0,
        "message": "success",
        "reason": "success",
        "data": "this is home/info page"
    }  
    ```
    """       
    return Reply.success("this is home/info page")