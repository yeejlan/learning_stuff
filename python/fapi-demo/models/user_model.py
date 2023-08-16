from enum import Enum, IntEnum
import db
from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import List

class UserStatus(IntEnum):
    normal = 1
    frozen = 2
    closed = 3

    def __int__(self):
        return self.value

    def __str__(self):
        return self.name

status_map = {member.name: member.value for member in UserStatus}
status_map_reversed = {v: k for k, v in status_map.items()}

def make_status_enum():
    attrs = {val: val for val in status_map_reversed.values()}
    NewEnum = Enum('UserStatusStr', attrs)
    return NewEnum

UserStatusStr = make_status_enum()

class UserModel(BaseModel):
    id: int
    name: str
    email: str|None
    password: str
    status: UserStatus
    note: str|None
    created_at: datetime|None
    updated_at: datetime|None

    @computed_field
    @property
    def status_str(self) -> str:
        return str(self.status)

    def api_dump(self):
        out = self.model_dump()
        del out['password']
        return out


async def get_user_by_id(user_id: int) -> UserModel:
    query = 'select * from users where id = %s'
    row = await db.select_one(query, user_id, to=UserModel)
    return row

async def list_users() -> List[UserModel]:
    query = 'select * from users where 1 limit 10'
    rows = await db.select(query, to=UserModel)
    return rows
 
async def update_user_status(user_id: int, user_status: int) -> int:
    query = 'update users set status = %s where id= %s'
    res = await db.update(query, user_status, user_id)
    return res