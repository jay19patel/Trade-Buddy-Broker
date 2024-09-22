from pydantic import BaseModel
from typing import Optional
from app.Models.models import CreateBy,OrderSide
class CreateNewOrder(BaseModel):
    stock_symbol:str
    order_side:OrderSide
    stock_isin:Optional[str] = None
    trigger_price:Optional[float] = None
    limit_price: Optional[float] = None
    stoploss_limit_price: float
    stoploss_trigger_price: float
    target_limit_price: float
    target_trigger_price: float
    quantity: Optional[int] = None
    created_by: CreateBy

class CreateOrder(BaseModel):
    position_id:Optional[str] = None,

    stock_symbol: str
    stock_isin: str

    order_side: Optional[str] = None
    order_types: Optional[str] = None
    product_type: Optional[str] = None

    quantity: Optional[int] = None
    trigger_price: Optional[float] = None
    limit_price: Optional[float] = None

    stop_order_hit: Optional[bool] = None

    stoploss_limit_price: Optional[float] = None
    stoploss_trigger_price: Optional[float] = None

    target_limit_price: Optional[float] = None
    target_trigger_price: Optional[float] = None
    created_by: Optional[str] = None 

