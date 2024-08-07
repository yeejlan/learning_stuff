from enum import IntEnum, StrEnum
import aiomysql
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Any, List

from core.cache import Cache
from core.core_model import CoreModel
from core.go_result import GoResult, catch_error_as_goresult
from core.exception import ModelException
from core.querybuilder import QueryBuilder
from core.resource_loader import getResourceLoader

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

class UserModel(CoreModel):
    id: int
    name: str
    email: str|None
    password: str = Field(exclude=True)
    status: UserStatus
    note: str|None
    created_at: datetime|None
    updated_at: datetime|None

    @computed_field
    @property
    def status_str(self) -> UserStatusStr: 
        return UserStatusStr.from_int(self.status)



def make_query_builder() -> QueryBuilder:
    pool = getResourceLoader().getMysqlPool('DB')
    return (QueryBuilder.new()
        .table('users')
        .map_query_to_model(UserModel)
        .set_conn_or_pool(pool)
    )

@Cache.memorize('UserInfo_{user_id}')
async def getUserById(user_id: int) -> UserModel:
    row = await (make_query_builder()
        .where('id', user_id)
        .exec_select_one()
    )
    return row

@Cache.memorize_many('UserInfo_{user_id}')
async def listUserByIds(ids: list[int]) -> list[UserModel]:
    rows = await (make_query_builder()
        .where_in('id', ids)
        .exec_select()
    )
    return rows

@Cache.memorize('list10Users')
async def listUsers() -> List[UserModel]:
    rows = await (make_query_builder()
        .limit(10)
        .exec_select()
    )
    return rows

@Cache.forget('list10Users')
@Cache.forget('UserInfo_{user_id}')
async def clearCache(user_id: int):
    pass

async def updateUserStatus(user_id: int, user_status: int) -> int:
    res = await (make_query_builder()
        .update('status', user_status)
        .where('id', user_id)
        .exec_update()
    )
    await clearCache(user_id)
    return res

async def createUser(user_data: dict):
    one = await (make_query_builder()
        .insert(user_data)
        .exec_insert_and_retrieve()
    )
    await clearCache(one.id)
    return one

async def deleteUser(user_id: int):
    res = await (make_query_builder()
        .delete()
        .where('id', user_id)
        .exec_delete()
    )
    await clearCache(user_id)
    return res

@catch_error_as_goresult()
async def updateFailed() -> GoResult:
    uid1 = 1
    uid2 = 11
    async def freeze2Users(conn: aiomysql.Connection):
        res1 = await (make_query_builder().set_conn_or_pool(conn)
                      .update('status', UserStatus.frozen)
                      .where('id', uid1)
                      .exec_update()
                      )
        raise ModelException('freeze2Users failed on purpose')
        res2 = await (make_query_builder().set_conn_or_pool(conn)
                      .update('status', UserStatus.frozen)
                      .where('id', uid2)
                      .exec_update()
                      )
        return [res1, res2]

    result = await make_query_builder().transaction(freeze2Users)
    await clearCache(uid1)
    await clearCache(uid2)    
    return result

        


@catch_error_as_goresult()
async def updateSuccess() -> GoResult:
    uid1 = 1
    uid2 = 11
    async def freeze2Users(conn: aiomysql.Connection):
        res1 = await (make_query_builder().set_conn_or_pool(conn)
                      .update('status', UserStatus.frozen)
                      .where('id', uid1)
                      .exec_update()
                      )
        res2 = await (make_query_builder().set_conn_or_pool(conn)
                      .update('status', UserStatus.frozen)
                      .where('id', uid2)
                      .exec_update()
                      )
        return [res1, res2]

    result = await make_query_builder().transaction(freeze2Users)
    await clearCache(uid1)
    await clearCache(uid2)    
    return result