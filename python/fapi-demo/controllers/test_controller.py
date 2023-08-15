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
            "example": 
                {
                    "name": "my name",
                    "price": 3.05,
                    "qty": 10
                }
        }
    }    

@router.post("/json", response_model=MyPayload)
async def test_json_params_validation(p: MyPayload):
    """
    Json payload and data validation.

    ```
    name: optional, min_length=3, max_length=20
    price: ge=1.05, le=100.67
    qty: int
    ```
    """        

    out = p.model_dump()
    out = {
        "name": "Foo",
        "price": 13.15, 
        "qty": 101,
        "ccc": 123,
    }
    return Reply.success(out)

class MyData(BaseModel):
    name: str
    password: str
    model_config = {
        "json_schema_extra": {
            "example":
{
  "code": 0,
  "message": "success",
  "reason": "success",
  "data": {
    "name": "the nama column"
  }
}
        }
    } 

    def api_dump(self):
        out = self.model_dump()
        del out['password']
        return out

@router.post('/data', response_model=MyData) 
async def test_data_rules():
    """
    Output data test, using api_dump() to hide 'password' field.
    """  
    out = {
        "name": "the nama column",
        "password": 'password should be hide', 
    }

    out = MyData(**out).api_dump()
    return Reply.success(out)


import pydantic_core 
@router.post('/all-errors') 
async def list_all_errors():
    """
    This function dose not exist, need change source code to make it work.
    """      
    return pydantic_core.list_all_errors()
