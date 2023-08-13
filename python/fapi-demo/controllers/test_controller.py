from typing import Generator
from fastapi import APIRouter, Depends
from reply import Reply
from exception import UserException

router = APIRouter()

@router.get("/user-err")
def test_user_exception(name: str, price: int):
    """
    Test UserException.

    ```
    {
        "name": "my name",  //The name of the item.
        "price": "12",      //The price of the item. 
    }  
    ```

    Output
    ```
    {
        "code": 1500,
        "message": "this is testing error",
        "reason": "operation_failed",
        "data": null
    }  
    ```
    """    
    raise UserException("this is testing error", Reply.OPERATION_FAILED)


@router.get("/err")
def test_unknown_error():
    """
    Test unknown error.

    Output
    ```
    {
        "code": 500,
        "message": "this is unknown error",
        "reason": "internal_server_error",
        "data": null
    }    
    ```
    """    
    raise Exception("this is unknown error")
