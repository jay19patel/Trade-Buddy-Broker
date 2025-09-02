"""
Account repository implementation
"""

from typing import List, Optional, Dict
from .base import BaseRepository
from trade_buddy.entities.models import Account
from trade_buddy.core.exceptions import DataNotFoundError, TradeBuddyException


class AccountRepository(BaseRepository[Account]):
    """Repository for Account entities"""
    
    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._email_index: Dict[str, str] = {}  # email -> account_id mapping
    
    async def create(self, account: Account) -> Account:
        """Create new account"""
        if account.account_id in self._accounts:
            raise TradeBuddyException(
                message="Account with this ID already exists",
                resolution="Use a different account ID"
            )
        
        if account.email_id in self._email_index:
            raise TradeBuddyException(
                message="Email address is already registered",
                resolution="Use a different email address"
            )
        
        self._accounts[account.account_id] = account
        self._email_index[account.email_id] = account.account_id
        return account
    
    async def get_by_id(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        return self._accounts.get(account_id)
    
    async def get_by_email(self, email: str) -> Optional[Account]:
        """Get account by email"""
        account_id = self._email_index.get(email)
        if account_id:
            return self._accounts.get(account_id)
        return None
    
    async def get_by_user_id(self, user_id: str) -> Optional[Account]:
        """Get account by user ID (email or account ID)"""
        # Try as account ID first
        account = await self.get_by_id(user_id)
        if account:
            return account
        
        # Try as email
        return await self.get_by_email(user_id)
    
    async def update(self, account: Account) -> Account:
        """Update account"""
        if account.account_id not in self._accounts:
            raise DataNotFoundError("Account", account.account_id)
        
        self._accounts[account.account_id] = account
        return account
    
    async def delete(self, account_id: str) -> bool:
        """Delete account"""
        if account_id not in self._accounts:
            return False
        
        account = self._accounts[account_id]
        del self._accounts[account_id]
        if account.email_id in self._email_index:
            del self._email_index[account.email_id]
        return True
    
    async def get_all(self) -> List[Account]:
        """Get all accounts"""
        return list(self._accounts.values())
    
    async def clear_all(self):
        """Clear all data (for testing)"""
        self._accounts.clear()
        self._email_index.clear()