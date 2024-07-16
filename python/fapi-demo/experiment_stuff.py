
from pydantic import Field
from core.core_model import CoreModel


class UserModel(CoreModel):
    id: int
    name: str
    email: str|None
    password: str = Field(exclude=True)


u = UserModel(id=1, name='nana', password = '1111', email='cc@dd')

print(u)
print(u.password)