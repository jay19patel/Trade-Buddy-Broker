"""
Account repository implementation
"""

from typing import List, Optional, Dict
from sqlmodel import select, update, delete
from .base import BaseRepository
from trade_buddy.entities.models import Account
from trade_buddy.core.exceptions import DataNotFoundError, TradeBuddyException
from trade_buddy.core.database import get_database_manager


class AccountRepository(BaseRepository[Account]):
    """Repository for Account entities"""
    
    async def create(self, account: Account) -> Account:
        """Create new account"""
        db = get_database_manager()
        async for session in db.get_session():
            # Check if account already exists
            stmt = select(Account).where(Account.account_id == account.account_id)
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                raise TradeBuddyException(
                    message="Account with this ID already exists",
                    resolution="Use a different account ID"
                )
            
            # Check if email already exists
            stmt = select(Account).where(Account.email_id == account.email_id)
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                raise TradeBuddyException(
                    message="Email address is already registered",
                    resolution="Use a different email address"
                )
            
            session.add(account)
            await session.commit()
            await session.refresh(account)
            return account
    
    async def get_by_id(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Account).where(Account.account_id == account_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Account]:
        """Get account by email"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Account).where(Account.email_id == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str) -> Optional[Account]:
        """Get account by user ID (email or account ID)"""
        # Try as account ID first
        account = await self.get_by_id(user_id)
        if account:
            return account
        
        # Try as email
        return await self.get_by_email(user_id)
    
    async def get_all(self) -> List[Account]:
        """Get all accounts"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Account)
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def update(self, account: Account) -> Account:
        """Update account"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = (
                update(Account)
                .where(Account.account_id == account.account_id)
                .values(**account.model_dump(exclude_unset=True))
            )
            await session.execute(stmt)
            await session.commit()
            
            # Return updated account
            stmt = select(Account).where(Account.account_id == account.account_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def delete(self, account_id: str) -> bool:
        """Delete account"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = delete(Account).where(Account.account_id == account_id)
            await session.execute(stmt)
            await session.commit()
            return True
    
    async def exists(self, account_id: str) -> bool:
        """Check if account exists"""
        account = await self.get_by_id(account_id)
        return account is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if account exists by email"""
        account = await self.get_by_email(email)
        return account is not None
    
    async def clear_all(self):
        """Clear all data (for testing)"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = delete(Account)
            await session.execute(stmt)
            await session.commit()