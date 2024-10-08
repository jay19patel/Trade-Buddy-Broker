
from fastapi import APIRouter,Depends,status
from uuid import uuid4
from sqlalchemy import select
from fastapi.responses import JSONResponse
# App
from app.Database.base import get_db, AsyncSession
from app.Schemas.transaction_schema import CreateTransaction
from app.Core.security import get_account_from_token
from app.Models.model import Transaction,Account,TransactionType
from app.Core.responseBytb import TBException,TBResponse
transaction_route =APIRouter()

@transaction_route.post("/create_transaction")
async def create_new_transaction(transaction_data:CreateTransaction,
                                 account:Account =Depends(get_account_from_token),
                                 db:AsyncSession =Depends(get_db)):
    try:
        transaction = Transaction(
            transaction_id=str(uuid4()), 
            account_id=account.account_id,
            transaction_type=transaction_data.transaction_type,
            transaction_amount=transaction_data.amount,
            transaction_note=transaction_data.note
        )

        # Update account balance
        if transaction.transaction_type == TransactionType.DEPOSIT:
            account.balance += transaction.transaction_amount
        elif transaction.transaction_type == TransactionType.WITHDRAW:
            if account.balance >= transaction.transaction_amount:
                account.balance -= transaction.transaction_amount
            else:
                raise Exception("Insufficient funds")
        
        print(account.balance)
        db.add_all([transaction,account])
        await db.commit()
        await db.refresh(transaction)
        await db.refresh(account)

        return TBResponse(
            message="Transaction successful",
            payload={"transaction_id": transaction.transaction_id}
        )
        
    except Exception as e:
        await db.rollback()
        raise TBException(
            message=str(e),
            resolution="Try Agin",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@transaction_route.get("/get_all_transactions")
async def get_all_transactions( account: Account = Depends(get_account_from_token),
                                db:AsyncSession =Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.account_id == account.account_id))
    transaction_list = result.scalars().all()
    return {"transaction_list":transaction_list,"total_balance":account.balance}