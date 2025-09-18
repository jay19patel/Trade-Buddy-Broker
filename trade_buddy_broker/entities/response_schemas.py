"""
Response schemas for Trade Buddy SDK
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


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
    trailing_stoploss: float
    trailing_target: float
    created_datetime: datetime
    # Margin stats
    total_margin: float
    utilized_margin: float
    available_margin: float
    margin_percentage: float
    default_leverage: float
    
    class Config:
        from_attributes = True


class LoginData(BaseModel):
    """Login response data schema"""
    user: UserData
    access_token: str
    session_id: str
    token_type: str = "bearer"
    
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
    trailing_stoploss: float
    trailing_target: float
    created_datetime: datetime
    # Margin stats
    total_margin: float
    utilized_margin: float
    available_margin: float
    margin_percentage: float
    default_leverage: float
    
    class Config:
        from_attributes = True


