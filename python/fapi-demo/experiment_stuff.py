import pickle
from typing import Any

def serialize_value(cls, value: Any) -> bytes:
    return pickle.dumps(value)

def unserialize_value(cls, data: bytes) -> Any:
    return pickle.loads(data)

from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# 序列化示例
data = {
    "name": "Alice",
    "age": 30,
    "user": User(name="Bob", age=25),
    "tags": ("tag1", "tag2"),
    "none_value": None
}

serialized = serialize_value(None, data)
print("Serialized:", serialized)

# 反序列化示例
deserialized = unserialize_value(None, serialized)
print("Deserialized:", deserialized)

