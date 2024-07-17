from datetime import datetime
from pydantic import BaseModel
from typing import Any, Dict

from core.time_util import ensure_default_timezone


class CoreModel(BaseModel):
    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__init__(**state)

    class Config:
        json_encoders = {
            datetime: lambda v: ensure_default_timezone(v).isoformat()
        }
