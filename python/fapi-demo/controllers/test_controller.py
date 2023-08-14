from typing import Generator
from fastapi import APIRouter, Depends
from fastapi.params import Body
from pydantic import BaseModel, Field
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

class MyPayload(BaseModel):
    name: str = Field(None, min_length=3, max_length=20)
    price: float = Field(..., ge=1.05, le=100.67) 
    qty: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "my name",
                    "price": 3.05,
                    "qty": 10
                }
            ]
        }
    }    

@router.post("/json")
def test_json_params_validation(p: MyPayload):
    """
    Test unknown error.

    ```
    name: optional, min_length=3, max_length=20
    price: ge=1.05, le=100.67
    qty: int
    ```
    
    Output
    ```
    {
        "code": 0,
        "message": "success",
        "reason": "success",
        "data": {
            "name": "my name",
            "price": 3.05,
            "qty": 10
        }
    }
    ```
    """        
    return Reply.success(p.model_dump())