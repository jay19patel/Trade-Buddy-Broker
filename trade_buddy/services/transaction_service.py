"""
Transaction management service
"""

from ..models import Account, Transaction, TransactionType
from ..schemas import TransactionSchema
from ..core.exceptions import InsufficientFundsError, ValidationError
from ..core.response import TradeBuddyResponse
from ..utils.security import SecurityManager
from .factory import RepositoryFactory


class TransactionService:
    """Transaction management service"""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.transaction_repo = repository_factory.get_transaction_repository()
        self.account_repo = repository_factory.get_account_repository()
        self.security = SecurityManager()
    
    async def create_transaction(self, account: Account, data: TransactionSchema) -> TradeBuddyResponse:
        """Create new transaction"""
        try:
            transaction_type = TransactionType.DEPOSIT if data.transaction_type.upper() == "DEPOSIT" else TransactionType.WITHDRAW
            
            # Validate withdrawal
            if transaction_type == TransactionType.WITHDRAW and data.amount > account.balance:
                raise InsufficientFundsError(account.balance)
            
            # Create transaction
            transaction = Transaction(
                transaction_id=self.security.generate_unique_id("TXN"),
                account_id=account.account_id,
                transaction_type=transaction_type,
                transaction_amount=data.amount,
                transaction_note=data.note
            )
            
            # Update account balance
            if transaction_type == TransactionType.DEPOSIT:
                account.balance += data.amount
            else:
                account.balance -= data.amount
            
            await self.transaction_repo.create(transaction)
            await self.account_repo.update(account)
            
            return TradeBuddyResponse(
                message=f"{transaction_type.value} completed successfully",
                payload={
                    "transaction_id": transaction.transaction_id,
                    "type": transaction_type.value,
                    "amount": data.amount,
                    "new_balance": round(account.balance, 2)
                }
            )
            
        except Exception as e:
            if isinstance(e, (InsufficientFundsError, ValidationError)):
                raise
            raise ValidationError(f"Transaction failed: {str(e)}")
    
    async def get_transaction_history(self, account: Account):
        """Get transaction history for account"""
        try:
            transactions = await self.transaction_repo.get_by_account(account.account_id)
            return [txn.to_dict() for txn in transactions]
        except Exception as e:
            raise Exception(f"Failed to retrieve transaction history: {str(e)}")