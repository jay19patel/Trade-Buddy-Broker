"""
Data models and enums for Trade Buddy SDK
"""

from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum


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


# Data Models
@dataclass
class Account:
    """Account model"""
    account_id: str
    full_name: str
    email_id: str
    password: str
    balance: float = 0.0
    email_verified: bool = False
    role: str = "User"
    is_activate: bool = True
    description: str = "Trade Buddy User"
    max_trad_per_day: int = 5
    base_stoploss: float = 0.0
    base_target: float = 0.0
    trailing_status: bool = True
    trailing_stoploss: float = 0.0
    trailing_target: float = 0.0
    created_datetime: datetime = field(default_factory=datetime.now)

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


@dataclass
class Position:
    """Position model"""
    position_id: str
    account_id: str
    stock_symbol: str
    stock_type: StockType
    position_status: PositionStatus = PositionStatus.PENDING
    position_side: OrderSide = OrderSide.BUY
    product_type: ProductType = ProductType.CNC
    buy_average: float = 0.0
    buy_margin: float = 0.0
    buy_quantity: int = 0
    sell_average: float = 0.0
    sell_margin: float = 0.0
    sell_quantity: int = 0
    pnl_total: float = 0.0
    target_price: float = 0.0
    stoploss_price: float = 0.0
    created_date: datetime = field(default_factory=datetime.now)
    created_by: CreateBy = CreateBy.MANUAL
    orders: List["Order"] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "position_id": self.position_id,
            "account_id": self.account_id,
            "stock_symbol": self.stock_symbol,
            "stock_type": self.stock_type.value,
            "position_status": self.position_status.value,
            "position_side": self.position_side.value,
            "product_type": self.product_type.value,
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
            "created_by": self.created_by.value,
            "orders": [order.to_dict() for order in self.orders]
        }


@dataclass
class Order:
    """Order model"""
    order_id: str
    account_id: str
    position_id: str
    stock_symbol: str
    order_side: OrderSide = OrderSide.BUY
    order_types: OrderTypes = OrderTypes.NewOrder
    product_type: ProductType = ProductType.CNC
    price: Optional[float] = None
    quantity: Optional[int] = None
    stop_order_hit: Optional[bool] = None
    stop_order_activate: bool = False
    stoploss_price: Optional[float] = None
    target_price: Optional[float] = None
    order_datetime: datetime = field(default_factory=datetime.now)
    created_by: CreateBy = CreateBy.MANUAL

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "order_id": self.order_id,
            "account_id": self.account_id,
            "position_id": self.position_id,
            "stock_symbol": self.stock_symbol,
            "order_side": self.order_side.value,
            "order_types": self.order_types.value,
            "product_type": self.product_type.value,
            "price": self.price,
            "quantity": self.quantity,
            "stop_order_hit": self.stop_order_hit,
            "stop_order_activate": self.stop_order_activate,
            "stoploss_price": self.stoploss_price,
            "target_price": self.target_price,
            "order_datetime": self.order_datetime.isoformat(),
            "created_by": self.created_by.value
        }


@dataclass
class Transaction:
    """Transaction model"""
    transaction_id: str
    account_id: str
    transaction_type: TransactionType
    transaction_amount: float
    transaction_note: str = ""
    transaction_datetime: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "transaction_id": self.transaction_id,
            "account_id": self.account_id,
            "transaction_type": self.transaction_type.value,
            "transaction_amount": self.transaction_amount,
            "transaction_note": self.transaction_note,
            "transaction_datetime": self.transaction_datetime.isoformat()
        }


@dataclass
class Ticket:
    """Support ticket model"""
    id: str
    email: str
    title: str
    message: str
    replied: bool = False
    datetime: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "title": self.title,
            "message": self.message,
            "replied": self.replied,
            "datetime": self.datetime.isoformat()
        }