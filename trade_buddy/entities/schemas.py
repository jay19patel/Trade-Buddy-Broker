"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from .models import OrderSide, CreateBy, StockType


class RegistrationSchema(BaseModel):
    """User registration schema"""
    email_id: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User password")
    full_name: str = Field(..., min_length=2, description="User's full name")
    max_trad_per_day: int = Field(default=5, ge=1, le=100)
    base_stoploss: float = Field(default=5.0, ge=0.1, le=50.0)
    base_target: float = Field(default=10.0, ge=0.1, le=100.0)
    trailing_status: bool = Field(default=True)
    trailing_stoploss: float = Field(default=10.0, ge=0.1, le=50.0)
    trailing_target: float = Field(default=10.0, ge=0.1, le=100.0)
    description: str = Field(default="Trade Buddy User")

    @field_validator('password')
    def validate_password(cls, v):
        if len(v.strip()) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class LoginSchema(BaseModel):
    """User login schema"""
    user_id: str = Field(..., description="Email or account ID")
    password: str = Field(..., description="User password")


class CreateOrderSchema(BaseModel):
    """Create new order schema"""
    stock_symbol: str = Field(..., min_length=1)
    order_side: OrderSide
    stock_type: StockType
    price: float = Field(..., gt=0)
    stoploss_price: float = Field(..., gt=0)
    target_price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    created_by: CreateBy = CreateBy.MANUAL

    @field_validator('stock_symbol')
    def validate_stock_symbol(cls, v):
        return v.upper().strip()


class UpdateStoplossSchema(BaseModel):
    """Update stoploss schema"""
    position_id: str
    stoploss_price: Optional[float] = Field(None, gt=0)
    target_price: Optional[float] = Field(None, gt=0)
    quantity: int = Field(..., gt=0)
    created_by: CreateBy = CreateBy.MANUAL


class UpdateQuantitySchema(BaseModel):
    """Update quantity schema"""
    position_id: str
    order_side: OrderSide
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    created_by: CreateBy = CreateBy.MANUAL


class ExitOrderSchema(BaseModel):
    """Exit order schema"""
    position_id: str
    price: float = Field(..., gt=0)
    created_by: CreateBy = CreateBy.MANUAL


class TransactionSchema(BaseModel):
    """Transaction schema"""
    transaction_type: str = Field(..., pattern="^(DEPOSIT|WITHDRAW)$")
    amount: float = Field(..., gt=0)
    note: str = Field(default="")


class SupportTicketSchema(BaseModel):
    """Support ticket schema"""
    email: EmailStr
    title: str = Field(..., min_length=3, max_length=100)
    message: str = Field(..., min_length=10, max_length=1000)