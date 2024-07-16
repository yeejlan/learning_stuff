import asyncio
from typing import Generator
from fastapi import APIRouter, Depends, Request
from fastapi.params import Body
from pydantic import BaseModel, Field
from core import deps, logger
from core.reply import Reply
from core.exception import FluxException, ModelException, UserException
from core.logger import get_logger
from core.request_context import getRequestContext
from core.user_session import UserSession

router = APIRouter()

@router.get("/user-err")
def test_user_exception():
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
    raise UserException("this is testing error", Reply.OPERATION_FAILED, {"a":1, "b":2})


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
    raise ModelException("this is unknown error")

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

@router.get('/log')
async def log_test():
    
    get_logger('err500').error('my app has an error')
    get_logger('my').warning('something dose not work')
    getRequestContext()['uid'] = 1234
    getLogger().info('log_test() is done')

    return "check log files please."  

def getLogger():
    return logger.get_logger(__name__)

from fastapi import BackgroundTasks, Depends

class JobManager:
    def __init__(self):
        self.error = None

    async def __aenter__(self):
        getLogger().debug(f"Starting job")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            getLogger().error(f"Job failed: {exc_value}")
            self.error = exc_value
        else:
            getLogger().debug(f"Job completed successfully")
        return False

@router.get("/bg-task")
async def send_notification(
    message: str, 
    background_tasks: BackgroundTasks
):
    getLogger().debug("before send_notification")
    getRequestContext()['task_id'] = 1001
    background_tasks.add_task(send_message, message)
    getLogger().debug("after send_notification")
    return {"message": "Message sent"}

async def send_message(msg: str):
    async with JobManager() as manager:
        await asyncio.sleep(3)
        for i in range(10):
            getLogger().info(f"bg_jobs: job doing: #{i}" )
            await asyncio.sleep(5)
        
        raise FluxException('bg_jobs: jobs not done!')  
        getLogger().info("bg_jobs: reach here")

@router.get("/sleep-10-seconds")
async def sleep_10_seconds():
    await asyncio.sleep(10)
    return {"message": "Done sleeping."}

async def get_user_id():
    try:
        yield 1 
    finally:
        print("clean up")

@router.get("/test-generator-with-exception")
async def test_generator_with_exception(id=Depends(get_user_id)):
    print("id=" + str(id))
    raise Exception("Error!")

@router.get("/session", dependencies=[deps.launchUserSession])
async def session(req: Request):
    count = UserSession.getInt('count')
    UserSession.set('count', count + 1)
    data = UserSession.get_all()
    return {
        'session_id': UserSession.getSessionId(),
        'count': count,
        'session_data': data,
    }

class MyCustomeException(FluxException):
    pass

@router.get("/custom-flux-exception")
async def custom_flux_exception():
    raise MyCustomeException('This exception should have "at" info')