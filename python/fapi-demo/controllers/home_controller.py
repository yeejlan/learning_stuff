from fastapi import APIRouter
from reply import Reply,reply_map,reply_map_reversed
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

@app.get("/response-code", tags=["home"], response_model=dict)
def list_all_response_code():
    return Reply.success({
        'map': reply_map,
        'map_reversed': reply_map_reversed,
    })