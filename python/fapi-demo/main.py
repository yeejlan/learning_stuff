from fastapi import FastAPI
from enum import StrEnum
from collections import namedtuple

from controllers import router

app = FastAPI(host="0.0.0.0", port=5000)
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello World~~"}


class Status(StrEnum):
    normal = 'normal'
    frozen = 'frozen'
    closed = 'closed'

    __int_map = {
        1: normal,
        2: frozen, 
        3: closed,
    }
    __str_map = {v: k for k, v in __int_map.items()}

    def __int__(self):
        return Status.__str_map[self.value]

    @staticmethod
    def fromInt(value):
        return Status.__int_map[value]
    
    @staticmethod
    def list_map():
        return Status.__int_map


def my_func():
  Result = namedtuple('Result', ['a', 'b'])
  result = Result(1, 2)
  return result


@app.get("/status/{status_name}")
async def get_model(status_name: Status):

    return {"status": status_name,
            "status.int": int(status_name),
            }

from reply import Reply

print(int(Reply.BAD_PARAM))
print(str(Reply.BAD_PARAM))

