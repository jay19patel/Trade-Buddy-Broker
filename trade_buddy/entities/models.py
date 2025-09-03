"""
Data models and enums for Trade Buddy SDK - SQLModel Implementation
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


# Enums
class OrderSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class PositionStatus(Enum):
    PENDING = 'Pending'
    COMPLETED = 'Completed'


class TransactionType(Enum):
    DEPOSIT = "Deposit"
    WITHDRAW = "Withdraw"


class OrderTypes(Enum):
    NewOrder = "New Order"
    StopLossOrder = "Stoploss Order"
    UpdateQtyOrder = "Update Quantity Order"
    ExitOrder = "Exit Order"


class CreateBy(Enum):
    MANUAL = "Manual"
    ALGO = "Algo"


class ProductType(Enum):
    CNC = 'CNC'
    INTRADAY = 'Intraday'
    MARGIN = 'Margin'


class StockType(Enum):
    STOCK = 'Stocks'
    OPTION = 'Option'


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
    created_datetime: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    positions: List["Position"] = Relationship(back_populates="account")
    orders: List["Order"] = Relationship(back_populates="account")
    transactions: List["Transaction"] = Relationship(back_populates="account")

    def to_dict(self):
        """Convert to dictionary (exclude password)"""
        return {
            "account_id": self.account_id,
            "full_name": self.full_name,
            "email_id": self.email_id,
            "balance": self.balance,
            "email_verified": self.email_verified,
            "role": self.role,
            "is_activate": self.is_activate,
            "description": self.description,
            "max_trad_per_day": self.max_trad_per_day,
            "base_stoploss": self.base_stoploss,
            "base_target": self.base_target,
            "trailing_status": self.trailing_status,
            "trailing_stoploss": self.trailing_stoploss,
            "trailing_target": self.trailing_target,
            "created_datetime": self.created_datetime.isoformat()
        }


class Position(SQLModel, table=True):
    """Position model with SQLModel"""
    __tablename__ = "positions"
    
    position_id: str = Field(primary_key=True, max_length=50)
    account_id: str = Field(foreign_key="accounts.account_id", max_length=50)
    stock_symbol: str = Field(max_length=50)
    stock_type: str = Field(max_length=20)  # StockType.value
    position_status: str = Field(default="Pending", max_length=20)  # PositionStatus.value
    position_side: str = Field(default="BUY", max_length=10)  # OrderSide.value
    product_type: str = Field(default="CNC", max_length=20)  # ProductType.value
    buy_average: float = Field(default=0.0)
    buy_margin: float = Field(default=0.0)
    buy_quantity: int = Field(default=0)
    sell_average: float = Field(default=0.0)
    sell_margin: float = Field(default=0.0)
    sell_quantity: int = Field(default=0)
    pnl_total: float = Field(default=0.0)
    target_price: float = Field(default=0.0)
    stoploss_price: float = Field(default=0.0)
    created_date: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(default="Manual", max_length=20)  # CreateBy.value
    
    # Relationships
    account: Optional[Account] = Relationship(back_populates="positions")
    orders: List["Order"] = Relationship(back_populates="position")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "position_id": self.position_id,
            "account_id": self.account_id,
            "stock_symbol": self.stock_symbol,
            "stock_type": self.stock_type,
            "position_status": self.position_status,
            "position_side": self.position_side,
            "product_type": self.product_type,
            "buy_average": self.buy_average,
            "buy_margin": self.buy_margin,
            "buy_quantity": self.buy_quantity,
            "sell_average": self.sell_average,
            "sell_margin": self.sell_margin,
            "sell_quantity": self.sell_quantity,
            "pnl_total": self.pnl_total,
            "target_price": self.target_price,
            "stoploss_price": self.stoploss_price,
            "created_date": self.created_date.isoformat(),
            "created_by": self.created_by,
            "orders": [order.to_dict() for order in (self.orders or [])]
        }


class Order(SQLModel, table=True):
    """Order model with SQLModel"""
    __tablename__ = "orders"
    
    order_id: str = Field(primary_key=True, max_length=50)
    account_id: str = Field(foreign_key="accounts.account_id", max_length=50)
    position_id: str = Field(foreign_key="positions.position_id", max_length=50)
    stock_symbol: str = Field(max_length=50)
    order_side: str = Field(default="BUY", max_length=10)  # OrderSide.value
    order_types: str = Field(default="New Order", max_length=30)  # OrderTypes.value
    product_type: str = Field(default="CNC", max_length=20)  # ProductType.value
    price: Optional[float] = Field(default=None)
    quantity: Optional[int] = Field(default=None)
    stop_order_hit: Optional[bool] = Field(default=None)
    stop_order_activate: bool = Field(default=False)
    stoploss_price: Optional[float] = Field(default=None)
    target_price: Optional[float] = Field(default=None)
    order_datetime: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(default="Manual", max_length=20)  # CreateBy.value
    
    # Relationships
    account: Optional[Account] = Relationship(back_populates="orders")
    position: Optional[Position] = Relationship(back_populates="orders")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "order_id": self.order_id,
            "account_id": self.account_id,
            "position_id": self.position_id,
            "stock_symbol": self.stock_symbol,
            "order_side": self.order_side,
            "order_types": self.order_types,
            "product_type": self.product_type,
            "price": self.price,
            "quantity": self.quantity,
            "stop_order_hit": self.stop_order_hit,
            "stop_order_activate": self.stop_order_activate,
            "stoploss_price": self.stoploss_price,
            "target_price": self.target_price,
            "order_datetime": self.order_datetime.isoformat(),
            "created_by": self.created_by
        }


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

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "transaction_id": self.transaction_id,
            "account_id": self.account_id,
            "transaction_type": self.transaction_type,
            "transaction_amount": self.transaction_amount,
            "transaction_note": self.transaction_note,
            "transaction_datetime": self.transaction_datetime.isoformat()
        }


class Ticket(SQLModel, table=True):
    """Support ticket model with SQLModel"""
    __tablename__ = "tickets"
    
    id: str = Field(primary_key=True, max_length=50)
    email: str = Field(max_length=100)
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    replied: bool = Field(default=False)
    created_datetime: datetime = Field(default_factory=datetime.now)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "title": self.title,
            "message": self.message,
            "replied": self.replied,
            "datetime": self.created_datetime.isoformat()  # Keep 'datetime' for backward compatibility
        }