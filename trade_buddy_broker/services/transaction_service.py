"""
Transaction management service
"""

from trade_buddy_broker.entities.models import Account, Transaction, TransactionType
from trade_buddy_broker.entities.schemas import TransactionSchema
from trade_buddy_broker.core.exceptions import InsufficientFundsError, ValidationError
from trade_buddy_broker.core.response import TBResponse
from trade_buddy_broker.utils.security import SecurityManager
from trade_buddy_broker.repositories.account_repository import AccountRepository
from trade_buddy_broker.repositories.transaction_repository import TransactionRepository


class TransactionService:
    """Transaction management service"""
    
    def __init__(self):
        self.transaction_repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.security = SecurityManager()
    
    async def create_transaction(self, account: Account, data: TransactionSchema) -> TBResponse:
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
                transaction_type=transaction_type.value,
                transaction_amount=data.amount,
                transaction_note=data.note
            )
            
            # Update account balance and recalculate margins
            if transaction_type == TransactionType.DEPOSIT:
                account.balance += data.amount
                # Update available margin after deposit
                utilized_margin = account.utilized_margin or 0.0
                account.available_margin = max(account.balance - utilized_margin, 0.0)
                account.margin_percentage = (utilized_margin / account.balance * 100) if account.balance > 0 else 0.0
            else:
                account.balance -= data.amount
                # Update available margin after withdrawal
                utilized_margin = account.utilized_margin or 0.0
                account.available_margin = max(account.balance - utilized_margin, 0.0)
                account.margin_percentage = (utilized_margin / account.balance * 100) if account.balance > 0 else 0.0
            
            await self.transaction_repo.create(transaction)
            await self.account_repo.update(account)
            
            return TBResponse(
                message=f"{transaction_type.value} completed successfully",
                data={
                    "transaction": transaction.model_dump(),
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
            # Serialize SQLModel instances
            return [t.model_dump() for t in transactions]
        except Exception as e:
            raise Exception(f"Failed to retrieve transaction history: {str(e)}")