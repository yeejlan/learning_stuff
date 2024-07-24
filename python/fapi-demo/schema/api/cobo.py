
from typing import List
from pydantic import Field
from core.core_model import CoreResult


class CoinInfo(CoreResult):
    coin: str = Field(..., description="货币名称")
    display_code: str = Field(..., description="显示代码")
    description: str = Field(..., description="货币描述")
    decimal: int = Field(..., description="小数位数")
    can_deposit: bool = Field(..., description="是否可以存款")
    can_withdraw: bool = Field(..., description="是否可以取款")
    require_memo: bool = Field(..., description="是否需要备注")
    minimum_deposit_threshold: str = Field(..., description="最小存款阈值")

# 定义包含货币信息列表的模型
class SupportedCoinsResult(CoreResult):
    data: List[CoinInfo] = Field(..., description="支持的货币列表")


if __name__ == "__main__":

    example_data = [
        {
            "coin": "TRON_USDT",
            "display_code": "USDT",
            "description": "Tether",
            "decimal": 6,
            "can_deposit": True,
            "can_withdraw": True,
            "require_memo": False,
            "minimum_deposit_threshold": "10000"
        },
        {
            "coin": "ETH_USDT",
            "display_code": "USDT",
            "description": "Tether",
            "decimal": 6,
            "can_deposit": True,
            "can_withdraw": True,
            "require_memo": False,
            "minimum_deposit_threshold": "0"
        },
    ]

    coin_info_list = [CoinInfo(**coin_info) for coin_info in example_data]
    supported_coins_result = SupportedCoinsResult(data=coin_info_list)
    print(supported_coins_result.model_dump_json(indent=4))