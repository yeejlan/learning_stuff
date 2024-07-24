from datetime import datetime
from pydantic import BaseModel
from typing import Any, Dict

from core.time_util import fallback_to_local_timezone


class CoreModel(BaseModel):
    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__init__(**state)

    class Config:
        json_encoders = {
            datetime: lambda v: fallback_to_local_timezone(v).isoformat()
        }


#read only attribute
class CoreResult(CoreModel):
    class Config:
        frozen = True


if __name__ == "__main__":
    class MyResult(CoreResult):
        name: str

    res = MyResult(name='nana')
    print(res.model_config)
    try:
        res.name = 'lucy'
    except ValueError as e:
        print(e)
