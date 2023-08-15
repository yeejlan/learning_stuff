from enum import Enum, IntEnum
import db
from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import List

class UserStatus(IntEnum):
    normal = 1
    frozen = 2
    closed = 3

    __map = {
        normal: 'normal',
        frozen: 'frozen', 
        closed: 'closed',
    }
    __map_r = {v: k for k, v in __map.items()} # type: ignore

    def __int__(self):
        return self.value

    def __str__(self):
        return UserStatus.__map[self.value] # type: ignore
    
    @staticmethod
    def fromStr(value):
        return UserStatus.__map_r[value] # type: ignore
    
    @staticmethod
    def list_map():
        return UserStatus.__map

    @staticmethod 
    def make_enum():
        attrs = {val: val for val in UserStatus.__map.values()} # type: ignore
        NewEnum = Enum('UserStatusStr', attrs)
        return NewEnum


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
        del out['id']
        return out


async def get_user_by_id(user_id: int) -> UserModel:
    query = 'select * from users where id = %s'
    row = await db.select_one(query, user_id, to=UserModel)
    return row

async def list_users() -> List[UserModel]:
    query = 'select * from users where 1 limit 10'
    rows = await db.select(query, to=UserModel)
    return rows