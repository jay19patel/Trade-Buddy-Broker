from pydantic import BaseModel
from typing import List
from datetime import datetime

class ReplyBase(BaseModel):
    message: str

class Reply(ReplyBase):
    id: int
    datetime: datetime
    ticket_id: str

class TicketCreate(BaseModel):
    email: str
    title: str
    message: str

class StatusUpdate(BaseModel):
    status: str


class Account(BaseModel):
    description: str
    account_id: str
    is_activate:bool
    balance:float
    full_name: str
    total_deposit: float
    total_withdrawal: float
    total_amount: float
    total_trades: int
    positive_trades: int
    negative_trades: int
    created_datetime: datetime
    
class AccountList(BaseModel):
    accounts: List[Account]
    totalPages: int