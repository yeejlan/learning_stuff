

from datetime import datetime
from pydantic import Field
from core.core_model import CoreModel
from core.time_util import fallback_to_local_timezone, now, now_as_iso8601, now_as_mysql_datetime, now_with_timezone


class UserModel(CoreModel):
    id: int
    name: str
    email: str|None
    password: str = Field(exclude=True)


u = UserModel(id=1, name='nana', password = '1111', email='cc@dd')

print(u)
print(now_with_timezone())
print(now_as_iso8601())

n = datetime.now()
nn = fallback_to_local_timezone(n)
print(now_as_mysql_datetime())
print(nn)