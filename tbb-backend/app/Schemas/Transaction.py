from pydantic import BaseModel
from typing import Optional
from app.Models.models import TransactionType
class CreateTransaction(BaseModel):
    amount: float
    note: Optional[str] = None
    transaction_type: TransactionType
