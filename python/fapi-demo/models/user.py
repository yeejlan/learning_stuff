import db
from pydantic import BaseModel
from datetime import datetime
from typing import List

class User(BaseModel):
    id: int
    name: str
    email: str|None
    password: str
    status: int
    note: str|None
    created_at: datetime|None
    updated_at: datetime|None

async def get_user_by_id(user_id: int) -> User:
    query = 'select * from users where id = %s'
    row = await db.select_one(query, user_id, to=User)
    return row

async def list_users() -> List[User]:
    query = 'select * from users where 1 limit 10'
    rows = await db.select(query, to=User)
    return rows