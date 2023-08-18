from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from exception import UserException
from reply import Reply
from models import user_model
from datetime import datetime

router = APIRouter()

@router.get("/find/{user_id:path}", response_model=user_model.UserModel)
async def get_user_by_id(user_id: int):
    row = await user_model.get_user_by_id(user_id)
    return Reply.success(row)

@router.get("/all", response_model=List[user_model.UserModel])
async def list_all_users():
    rows = await user_model.list_users()
    return Reply.success(rows)

class UpdateUserStatusIn(BaseModel):
    user_id: int
    user_status: user_model.UserStatusStr

@router.post("/update-user-status", response_model=int)
async def update_user_status(p: UpdateUserStatusIn):
    status = int(p.user_status)
    res = await user_model.update_user_status(p.user_id, status)

    return Reply.success(res)

@router.get("/list-user-status", response_model=user_model.UserStatusStr)
async def list_user_status():
    res = user_model.status_map_reversed
    return Reply.success(res)

class CreateUserIn(BaseModel):
    name: str
    email: str|None
    password: str
    status: user_model.UserStatusStr

    def dict_dump(self):
        d = self.model_dump()
        d['status'] = int(d['status'])
        return d

@router.post("/create-user", response_model=user_model.UserModel)
async def create_user(user: CreateUserIn):
    one = await user_model.create_user(user.dict_dump())
    return Reply.success(one)