from pydantic import BaseModel
from typing import Any, Dict

class CoreModel(BaseModel):
    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__init__(**state)
