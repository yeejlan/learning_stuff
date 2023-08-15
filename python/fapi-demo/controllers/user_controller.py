from typing import List
from fastapi import APIRouter
from reply import Reply
from models import user_model

router = APIRouter()

@router.get("/find/{user_id:path}", response_model=user_model.UserModel)
async def get_user_by_id(user_id: int):
    row = await user_model.get_user_by_id(user_id)
    return Reply.success(row)

@router.get("/all", response_model=List[user_model.UserModel])
async def list_all_users():
    rows = await user_model.list_users()
    return Reply.success(rows)

@router.get("/list-user-status", response_model=user_model.UserStatus.make_enum())
async def list_user_status():
    res = user_model.UserStatus.list_map()
    return Reply.success(res)


@router.post("/update-user-status", response_model=int)
async def update_user_status(user_id: int, user_status: user_model.UserStatusStr):
    status = user_model.UserStatus.fromStr(user_status.value)
    res = await user_model.update_user_status(user_id, status)
    return Reply.success(res)