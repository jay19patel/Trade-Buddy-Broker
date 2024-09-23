from pydantic import BaseModel
from typing import Optional
from app.Models.models import CreateBy,OrderSide

class CreateNewOrder(BaseModel):
    stock_symbol:str
    order_side:OrderSide
    stock_isin:Optional[str] = None
    trigger_price:float
    limit_price: float
    stoploss_limit_price: float
    stoploss_trigger_price: float
    target_limit_price: float
    target_trigger_price: float
    quantity: int
    created_by: CreateBy
    
class CreateStoplossOrder(BaseModel):
    position_id:str
    stoploss_limit_price: Optional[float] = None
    stoploss_trigger_price: Optional[float] = None
    target_limit_price: Optional[float] = None
    target_trigger_price: Optional[float] = None
    quantity: int
    created_by: CreateBy 

class AddQuantityOrder(BaseModel):
    position_id: str
    order_side:OrderSide
    quantity: int
    limit_price: float
    created_by: CreateBy

class CreateExitOrder(BaseModel):
    position_id: str
    order_side:OrderSide
    quantity: int
    limit_price: float
    created_by: CreateBy
    


