"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegistrationSchema(BaseModel):
    """User registration schema"""
    email_id: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User password")
    full_name: str = Field(..., min_length=2, description="User's full name")
    max_trad_per_day: int = Field(default=5, ge=1, le=100)
    base_stoploss: float = Field(default=5.0, ge=0.1, le=50.0)
    base_target: float = Field(default=10.0, ge=0.1, le=100.0)
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


class TransactionSchema(BaseModel):
    """Transaction schema"""
    transaction_type: str = Field(..., pattern="^(DEPOSIT|WITHDRAW)$")
    amount: float = Field(..., gt=0)
    note: str = Field(default="")


class OpenPositionSchema(BaseModel):
    symbol_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    side: str = Field(..., pattern="^(BUY|SELL)$")
    stoploss: Optional[float] = Field(default=None, gt=0)
    target: Optional[float] = Field(default=None, gt=0)


class UpdatePositionLevelsSchema(BaseModel):
    position_id: str = Field(..., min_length=3)
    stoploss: Optional[float] = Field(default=None, gt=0)
    target: Optional[float] = Field(default=None, gt=0)


class ExitPositionSchema(BaseModel):
    position_id: str = Field(..., min_length=3)
    exit_price: float = Field(..., gt=0)


