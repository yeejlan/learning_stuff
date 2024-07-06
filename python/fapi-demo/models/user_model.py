from enum import IntEnum, StrEnum
import db
from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import List

from querybuilder import QueryBuilder

class UserStatus(IntEnum):
    normal = 1
    frozen = 2
    closed = 3

class UserStatusStr(StrEnum):
    normal = 'normal'
    frozen = 'frozen'
    closed = 'closed'

    def __int__(self):
        return UserStatus[self.name].value

    @classmethod
    def from_int(cls, value):
        return cls(UserStatus(value).name)

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
    def status_str(self) -> UserStatusStr:  # type: ignore
        return UserStatusStr.from_int(self.status)

    def api_dump(self):
        out = self.model_dump()
        del out['password']
        return out


def make_query_builder() -> QueryBuilder:
    return (QueryBuilder.new()
        .table('users')
        .map_query_to_model(UserModel)
        .use_pool_function(db.get_pool)
    )

async def getUserById(user_id: int) -> UserModel:
    row = await (make_query_builder()
        .where('id', user_id)
        .exec_select_one()
    )
    return row

async def listUsers() -> List[UserModel]:
    rows = await (make_query_builder()
        .limit(10)
        .exec_select()
    )
    return rows
 
async def updateUserStatus(user_id: int, user_status: int) -> int:
    res = await (make_query_builder()
        .update('status', user_status)
        .where('id', user_id)
        .exec_update()
    )
    return res

async def createUser(user_data: dict):
    one = await (make_query_builder()
        .insert_with_timestamp(user_data)
        .exec_insert_and_retrieve()
    )
    return one

async def deleteUser(user_id: int):
    res = await (make_query_builder()
        .delete()
        .where('id', user_id)
        .exec_delete()
    )
    return res