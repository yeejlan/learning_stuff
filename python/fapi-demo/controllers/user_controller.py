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
    row = await user_model.getUserById(user_id)
    return Reply.success(row)

@router.get("/list_users", response_model=List[user_model.UserModel])
async def list_users():
    rows = await user_model.listUsers()
    return Reply.success(rows)

class UpdateUserStatusIn(BaseModel):
    user_id: int
    user_status: user_model.UserStatusStr

@router.post("/update-user-status", response_model=int)
async def update_user_status(p: UpdateUserStatusIn):
    status = int(p.user_status)
    res = await user_model.updateUserStatus(p.user_id, status)

    return Reply.success(res)

class CreateUserIn(BaseModel):
    name: str
    email: str|None
    password: str
    status: user_model.UserStatusStr

    def as_dict(self):
        d = self.model_dump()
        d['status'] = int(d['status'])
        return d

@router.post("/create-user", response_model=user_model.UserModel)
async def create_user(user: CreateUserIn):
    one = await user_model.createUser(user.as_dict())
    return Reply.success(one)

class DeleteUserIn(BaseModel):
    user_id: int

@router.post("/delete-user", response_model=int)
async def delete_user(p: DeleteUserIn):
    res = await user_model.deleteUser(p.user_id)
    return Reply.success(res)