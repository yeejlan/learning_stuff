from fastapi import APIRouter
from reply import Reply
from app import app

@app.get("/", tags=["home"])
def homepage():
    """
    Homepage.

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
