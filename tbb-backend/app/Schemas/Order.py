from pydantic import BaseModel
from typing import Optional
from app.Models.models import CreateBy,OrderSide,StockType

class CreateNewOrder(BaseModel):
    stock_symbol:str
    order_side:OrderSide
    stock_type:StockType
    price:float
    stoploss_price: float
    target_price: float
    quantity: int
    created_by: CreateBy
    
class CreateStoplossOrder(BaseModel):
    position_id:str
    stoploss_price: Optional[float] = None
    target_price: Optional[float] = None
    quantity: int
    created_by: CreateBy 

class AddQuantityOrder(BaseModel):
    position_id: str
    order_side:OrderSide
    quantity: int
    price: float
    created_by: CreateBy

class CreateExitOrder(BaseModel):
    position_id: str
    order_side:OrderSide
    quantity: int
    price: float
    created_by: CreateBy
    


