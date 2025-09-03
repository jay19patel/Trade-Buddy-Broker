"""
Response schemas for Trade Buddy SDK
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class TBResponse(BaseModel):
    """
    Standard response format for all Trade Buddy broker methods
    """
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    
    class Config:
        from_attributes = True


class UserData(BaseModel):
    """User data schema for registration/login responses"""
    account_id: str
    full_name: str
    email_id: str
    balance: float
    email_verified: bool
    role: str
    is_activate: bool
    description: str
    max_trad_per_day: int
    base_stoploss: float
    base_target: float
    trailing_status: bool
    trailing_stoploss: float
    trailing_target: float
    created_datetime: datetime
    
    class Config:
        from_attributes = True


class LoginData(BaseModel):
    """Login response data schema"""
    user: UserData
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        from_attributes = True


class OrderData(BaseModel):
    """Order response data schema"""
    order_id: str
    account_id: str
    position_id: str
    stock_symbol: str
    order_side: str
    order_types: str
    product_type: str
    price: Optional[float]
    quantity: Optional[int]
    stop_order_hit: Optional[bool]
    stop_order_activate: bool
    stoploss_price: Optional[float]
    target_price: Optional[float]
    order_datetime: datetime
    created_by: str
    
    class Config:
        from_attributes = True


class PositionData(BaseModel):
    """Position response data schema"""
    position_id: str
    account_id: str
    stock_symbol: str
    stock_type: str
    position_status: str
    position_side: str
    product_type: str
    buy_average: float
    buy_margin: float
    buy_quantity: int
    sell_average: float
    sell_margin: float
    sell_quantity: int
    pnl_total: float
    target_price: float
    stoploss_price: float
    created_date: datetime
    created_by: str
    orders: List[OrderData] = []
    
    class Config:
        from_attributes = True


class TransactionData(BaseModel):
    """Transaction response data schema"""
    transaction_id: str
    account_id: str
    transaction_type: str
    transaction_amount: float
    transaction_note: str
    transaction_datetime: datetime
    
    class Config:
        from_attributes = True


class TicketData(BaseModel):
    """Support ticket response data schema"""
    id: str
    email: str
    title: str
    message: str
    replied: bool
    datetime: datetime
    
    class Config:
        from_attributes = True


class PositionsOverview(BaseModel):
    """Positions overview data schema"""
    total_positions: int
    active_positions: int
    completed_positions: int
    total_pnl: float
    total_investment: float
    positions: List[PositionData] = []
    
    class Config:
        from_attributes = True


class AccountData(BaseModel):
    """Account details response data schema"""
    account_id: str
    full_name: str
    email_id: str
    balance: float
    email_verified: bool
    role: str
    is_activate: bool
    description: str
    max_trad_per_day: int
    base_stoploss: float
    base_target: float
    trailing_status: bool
    trailing_stoploss: float
    trailing_target: float
    created_datetime: datetime
    
    class Config:
        from_attributes = True


class SymbolData(BaseModel):
    """Symbol search data schema"""
    symbol_id: str
    symbol_name: str
    symbol_type: str
    
    class Config:
        from_attributes = True


class PriceData(BaseModel):
    """Live price data schema"""
    symbol_id: str
    symbol_type: str
    ltp: float
    open_price: float
    high_price: float
    low_price: float
    prev_close: float
    change: float
    change_percent: float
    
    class Config:
        from_attributes = True