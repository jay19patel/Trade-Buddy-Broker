from sqlmodel import SQLModel, Field, Column, DateTime, Text, Float, Integer, Boolean
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum
import uuid

class TransactionType(str, Enum):
    """Transaction type enumeration"""
    DEPOSIT = "Deposit"
    WITHDRAW = "Withdraw"
    BUY = "Buy"
    SELL = "Sell"

class PositionType(str, Enum):
    """Position type enumeration"""
    LONG = "LONG"
    SHORT = "SHORT"

class PositionStatus(str, Enum):
    """Position status enumeration"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PENDING = "PENDING"

class NotificationType(str, Enum):
    """Notification type enumeration"""
    TRANSACTION = "TRANSACTION"
    POSITION = "POSITION"
    ERROR = "ERROR"
    SYSTEM = "SYSTEM"

class NotificationStatus(str, Enum):
    """Notification status enumeration"""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

class Account(SQLModel, table=True):
    """Account model"""
    __tablename__ = "accounts"
    
    account_id: str = Field(primary_key=True)
    full_name: str
    email_id: str = Field(unique=True, index=True)
    password_hash: str
    balance: float = Field(default=0.0)
    email_verified: bool = Field(default=False)
    role: str = Field(default="User")
    is_activate: bool = Field(default=True)
    description: Optional[str] = None
    max_trad_per_day: int = Field(default=5)
    base_stoploss: float = Field(default=0.0)
    base_target: float = Field(default=0.0)
    trailing_status: bool = Field(default=True)
    trailing_stoploss: float = Field(default=0.0)
    trailing_target: float = Field(default=0.0)
    created_datetime: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    default_leverage: float = Field(default=1.0)
    
    # Margin management fields
    total_margin: float = Field(default=0.0)
    utilized_margin: float = Field(default=0.0)
    available_margin: float = Field(default=0.0)
    margin_percentage: float = Field(default=0.0)
    
    @property
    def password(self) -> str:
        """Alias for password_hash for backward compatibility"""
        return self.password_hash
    
    def model_dump_safe(self) -> Dict[str, Any]:
        """Safe model dump excluding sensitive fields"""
        data = self.model_dump()
        # Remove sensitive fields
        data.pop('password_hash', None)
        data.pop('password', None)
        return data

class Transaction(SQLModel, table=True):
    """Transaction model"""
    __tablename__ = "transactions"
    
    transaction_id: str = Field(primary_key=True)
    account_id: str = Field(foreign_key="accounts.account_id")
    transaction_type: TransactionType
    transaction_amount: float
    transaction_note: Optional[str] = None
    transaction_datetime: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Position(SQLModel, table=True):
    """Position model with advanced features"""
    __tablename__ = "positions"
    
    position_id: str = Field(primary_key=True)
    account_id: str = Field(foreign_key="accounts.account_id")
    symbol_id: str
    side: str  # BUY/SELL
    position_type: PositionType = PositionType.LONG
    quantity: float
    avg_price: float
    invested_amount: float
    leverage: float = Field(default=1.0)
    margin_used: float = Field(default=0.0)
    trading_fee: float = Field(default=0.0)
    status: PositionStatus = PositionStatus.OPEN
    
    # Risk management
    stoploss: Optional[float] = None
    target: Optional[float] = None
    
    # Performance metrics
    pnl: Optional[float] = None
    pnl_percentage: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    realized_pnl: Optional[float] = None
    
    # Timestamps
    opened_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None
    exit_price: Optional[float] = None
    
    # Strategy info
    strategy_name: Optional[str] = None
    notes: Optional[str] = None
    
    # Advanced features - Pyramiding
    original_quantity: float = Field(default=0.0)
    total_quantity: float = Field(default=0.0)
    average_entry_price: float = Field(default=0.0)
    pyramid_count: int = Field(default=0)
    
    # Advanced features - Trailing
    trailing_count: int = Field(default=0)
    remaining_quantity: float = Field(default=0.0)
    average_exit_price: float = Field(default=0.0)

class Notification(SQLModel, table=True):
    """Notification model for storing all types of notifications"""
    __tablename__ = "notifications"
    
    notification_id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    account_id: str = Field(foreign_key="accounts.account_id")
    notification_type: NotificationType
    title: str
    message: str
    data: Optional[str] = Field(default=None, sa_column=Column(Text))  # Store as JSON string
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # For error notifications
    error_class: Optional[str] = None
    error_function: Optional[str] = None
    error_file: Optional[str] = None
    error_line: Optional[int] = None

class Session(SQLModel, table=True):
    """Session model"""
    __tablename__ = "sessions"
    
    session_id: str = Field(primary_key=True)
    account_id: str = Field(foreign_key="accounts.account_id")
    email: str
    full_name: str
    balance: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    device_info: Optional[str] = None
    ip_address: Optional[str] = None