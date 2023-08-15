import db
from pydantic import BaseModel
from datetime import datetime
from typing import List

class UserModel(BaseModel):
    id: int
    name: str
    email: str|None
    password: str
    status: int
    note: str|None
    created_at: datetime|None
    updated_at: datetime|None

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