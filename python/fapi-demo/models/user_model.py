from enum import Enum, IntEnum
import db
from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import List

from querybuilder import QueryBuilder

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

    def __str__(self):
        return self.value
    
    def __int__(self):
        return status_map[self.value]
    
    NewEnum.__str__ = __str__
    NewEnum.__int__ = __int__
    
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
    def status_str(self) -> UserStatusStr:  # type: ignore
        return str(self.status)

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

async def get_user_by_id(user_id: int) -> UserModel:
    row = await (make_query_builder()
        .where('id', user_id)
        .exec_select_one()
    )
    return row

async def list_users() -> List[UserModel]:
    rows = await (make_query_builder()
        .limit(10)
        .exec_select()
    )
    return rows
 
async def update_user_status(user_id: int, user_status: int) -> int:
    res = await (make_query_builder()
        .update('status', user_status)
        .where('id', user_id)
        .exec_update()
    )
    return res

async def create_user(user_data: dict):
    one = await (make_query_builder()
        .insert_with_timestamp(user_data)
        .exec_insert_and_retrieve()
    )
    return one

async def delete_user(user_id: int):
    res = await (make_query_builder()
        .delete()
        .where('id', user_id)
        .exec_delete()
    )
    return res