from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from core.exception import UserException
from core.reply import Reply
from models import holding_model
from datetime import datetime


router = APIRouter()

@router.get("/find/{request_id:path}", response_model=holding_model.HoldingInfo)
async def get_holdinginfo_by_id(request_id: int):
    row = await holding_model.getHoldingInfoById(request_id)
    return Reply.success(row)

@router.get("/list_holdings", response_model=List[holding_model.HoldingInfo])
async def list_holdings():
    rows = await holding_model.listHoldings()
    return Reply.success(rows)
