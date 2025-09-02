"""
Transaction repository implementation
"""

from typing import List, Optional, Dict
from .base import BaseRepository
from ..models import Transaction
from ..core.exceptions import DataNotFoundError


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction entities"""
    
    def __init__(self):
        self._transactions: Dict[str, Transaction] = {}
        self._account_index: Dict[str, List[str]] = {}  # account_id -> [transaction_ids]
    
    async def create(self, transaction: Transaction) -> Transaction:
        """Create new transaction"""
        self._transactions[transaction.transaction_id] = transaction
        
        # Update account index
        if transaction.account_id not in self._account_index:
            self._account_index[transaction.account_id] = []
        self._account_index[transaction.account_id].append(transaction.transaction_id)
        
        return transaction
    
    async def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self._transactions.get(transaction_id)
    
    async def get_by_account(self, account_id: str) -> List[Transaction]:
        """Get transactions by account ID"""
        transaction_ids = self._account_index.get(account_id, [])
        return [self._transactions[txn_id] for txn_id in transaction_ids if txn_id in self._transactions]
    
    async def update(self, transaction: Transaction) -> Transaction:
        """Update transaction"""
        if transaction.transaction_id not in self._transactions:
            raise DataNotFoundError("Transaction", transaction.transaction_id)
        
        self._transactions[transaction.transaction_id] = transaction
        return transaction
    
    async def delete(self, transaction_id: str) -> bool:
        """Delete transaction"""
        if transaction_id not in self._transactions:
            return False
        
        transaction = self._transactions[transaction_id]
        del self._transactions[transaction_id]
        
        # Update account index
        if transaction.account_id in self._account_index:
            if transaction_id in self._account_index[transaction.account_id]:
                self._account_index[transaction.account_id].remove(transaction_id)
        
        return True
    
    async def get_all(self) -> List[Transaction]:
        """Get all transactions"""
        return list(self._transactions.values())
    
    async def clear_all(self):
        """Clear all data (for testing)"""
        self._transactions.clear()
        self._account_index.clear()