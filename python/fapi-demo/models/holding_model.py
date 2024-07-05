from enum import Enum, IntEnum
import db
from pydantic import BaseModel, computed_field, Field
from datetime import datetime
from typing import List, Optional

from querybuilder import QueryBuilder

class Redeem(BaseModel):
    asset: str
    amount: str

class Refund(BaseModel):
    at: datetime
    asset: str
    amount: str

class Product(BaseModel):
    name: str = Field(..., description="Product name, only ASCII allowed")
    asset: str = Field(..., description="Product asset, USD EUR etc")
    redeem_at: datetime = Field(..., description="Expected redeem time")

class Detail(BaseModel):
    redeem: Optional[Redeem] = None
    refund: Optional[Refund] = None
    product: Optional[Product] = None

class ProductInfo(BaseModel):
    id: int
    name: str
    type: int
    asset: str
    schedule_at: datetime
    published_at: datetime
    last_edit_at: datetime
    ref_price: str
    ref_annualized_return: str
    listing_at: datetime
    delisting_at: datetime
    open_at: datetime
    close_at: datetime
    redeem_at: datetime
    redeem_n_days: int
    confirm_n_days: int
    fee_rate: str
    fee_rate_partner: str
    exit_fee_rate: str
    exit_fee_rate_partner: str
    min_amount: str
    delta_amount: str
    total_amount_limit: str
    max_amount: str
    exit_price: str
    purchase_type: int
    holiday_type: int
    cutoff: str
    tags: str  # 注意：这里可能需要自定义验证器来解析JSON字符串
    desc_en: Optional[str] = None
    desc_zh: Optional[str] = None
    status: int
    enabled: int
    created_at: datetime
    updated_at: datetime

class HoldingInfo(BaseModel):
    unique_id: int
    broker_id: int
    product_id: int
    batch_id: int
    request_id: str
    type: int
    asset: str
    amount: str
    fee: str
    exit_fee: str
    status: int
    step: int
    detail: Detail
    memo: Optional[str] = None
    confirm_at: datetime
    confirm_delay: int
    confirmed_at: Optional[datetime] = None
    redeem_at: datetime
    redeemed_at: Optional[datetime] = None
    holding_days: int
    expected_interest_rate: str
    expected_revenue: str
    real_interest_rate: Optional[str] = None
    real_revenue: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    product_info: ProductInfo
    status_str: str
    step_str: str


def make_query_builder() -> QueryBuilder:
    return (QueryBuilder.new()
        .table('users')
        .map_query_to_model(HoldingInfo)
        .use_pool_function(db.get_pool)
    )

async def getHoldingInfoById(request_id: int) -> HoldingInfo:
    row = await (make_query_builder()
        .where('request_id', request_id)
        .exec_select_one()
    )
    return row

async def listHoldings() -> List[HoldingInfo]:
    rows = await (make_query_builder()
        .limit(10)
        .exec_select()
    )
    return rows
 