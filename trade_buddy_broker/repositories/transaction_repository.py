"""
Transaction repository implementation
"""

from typing import List, Optional, Dict
from sqlmodel import select, delete
from .base import BaseRepository
from trade_buddy_broker.entities.models import Transaction
from trade_buddy_broker.core.exceptions import DataNotFoundError
from trade_buddy_broker.core.database import get_database_manager


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction entities"""
    
    async def create(self, transaction: Transaction) -> Transaction:
        """Create new transaction"""
        db = get_database_manager()
        async for session in db.get_session():
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            return transaction
    
    async def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_by_account(self, account_id: str, limit: int = 100) -> List[Transaction]:
        """Get transactions for an account"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = (
                select(Transaction)
                .where(Transaction.account_id == account_id)
                .order_by(Transaction.transaction_datetime.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def get_all(self) -> List[Transaction]:
        """Get all transactions"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Transaction).order_by(Transaction.transaction_datetime.desc())
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def update(self, transaction: Transaction) -> Transaction:
        """Update transaction"""
        db = get_database_manager()
        async for session in db.get_session():
            # For transactions, we typically don't update them once created
            # But if needed, we can implement this
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            return transaction
    
    async def delete(self, transaction_id: str) -> bool:
        """Delete transaction"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = delete(Transaction).where(Transaction.transaction_id == transaction_id)
            await session.execute(stmt)
            await session.commit()
            return True
    
    async def clear_all(self):
        """Clear all data (for testing)"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = delete(Transaction)
            await session.execute(stmt)
            await session.commit()