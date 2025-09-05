"""
Data models and enums for Trade Buddy SDK - SQLModel Implementation
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


# Enums
class TransactionType(Enum):
    DEPOSIT = "Deposit"
    WITHDRAW = "Withdraw"


# SQLModel Database Tables
class Account(SQLModel, table=True):
    """Account model with SQLModel"""
    __tablename__ = "accounts"
    
    account_id: str = Field(primary_key=True, max_length=50)
    full_name: str = Field(max_length=100)
    email_id: str = Field(unique=True, max_length=100)
    password: str = Field(max_length=255)
    balance: float = Field(default=0.0)
    email_verified: bool = Field(default=False)
    role: str = Field(default="User", max_length=50)
    is_activate: bool = Field(default=True)
    description: str = Field(default="Trade Buddy User", max_length=255)
    max_trad_per_day: int = Field(default=5)
    base_stoploss: float = Field(default=0.0)
    base_target: float = Field(default=0.0)
    trailing_status: bool = Field(default=True)
    trailing_stoploss: float = Field(default=0.0)
    trailing_target: float = Field(default=0.0)
    default_leverage: float = Field(default=1.0)
    created_datetime: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="account")

    def model_dump_safe(self):
        """Convert to dictionary (exclude password)"""
        data = self.model_dump()
        data.pop('password', None)  # Remove password from response
        return data


class Transaction(SQLModel, table=True):
    """Transaction model with SQLModel"""
    __tablename__ = "transactions"
    
    transaction_id: str = Field(primary_key=True, max_length=50)
    account_id: str = Field(foreign_key="accounts.account_id", max_length=50)
    transaction_type: str = Field(max_length=20)  # TransactionType.value
    transaction_amount: float = Field()
    transaction_note: str = Field(default="", max_length=255)
    transaction_datetime: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    account: Optional[Account] = Relationship(back_populates="transactions")


class Session(SQLModel, table=True):
    """User session model for authentication tracking"""
    __tablename__ = "sessions"
    
    session_id: str = Field(primary_key=True, max_length=100)
    account_id: str = Field(foreign_key="accounts.account_id", max_length=50)
    jwt_token: str = Field(max_length=500)
    device_info: Optional[str] = Field(default=None, max_length=200)
    ip_address: Optional[str] = Field(default=None, max_length=50)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field()
    
    # Relationship
    account: Optional[Account] = Relationship()


class PositionType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(Enum):
    OPEN = "Open"
    CLOSED = "Closed"


class Position(SQLModel, table=True):
    """Trading position model"""
    __tablename__ = "positions"
    
    position_id: str = Field(primary_key=True, max_length=50)
    account_id: str = Field(foreign_key="accounts.account_id", max_length=50)
    symbol_id: str = Field(max_length=100)
    side: str = Field(max_length=10)  # BUY/SELL
    position_type: str = Field(default=PositionType.LONG.value, max_length=10)
    quantity: float = Field()
    avg_price: float = Field()
    invested_amount: float = Field(default=0.0)
    leverage: float = Field(default=1.0)
    margin_used: float = Field(default=0.0)
    trading_fee: float = Field(default=0.0)
    status: str = Field(default=PositionStatus.OPEN.value, max_length=10)
    opened_at: datetime = Field(default_factory=datetime.now)
    closed_at: Optional[datetime] = Field(default=None)
    exit_price: Optional[float] = Field(default=None)
    pnl: Optional[float] = Field(default=None)
    pnl_percentage: Optional[float] = Field(default=None)
    unrealized_pnl: Optional[float] = Field(default=None)
    realized_pnl: Optional[float] = Field(default=None)
    stoploss: Optional[float] = Field(default=None)
    target: Optional[float] = Field(default=None)
    strategy_name: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)

    # Pyramiding / Trailing
    original_quantity: float = Field(default=0.0)
    total_quantity: float = Field(default=0.0)
    average_entry_price: float = Field(default=0.0)
    pyramid_count: int = Field(default=0)
    trailing_count: int = Field(default=0)
    remaining_quantity: float = Field(default=0.0)
    average_exit_price: float = Field(default=0.0)
    
    # Relationship
    account: Optional[Account] = Relationship()

