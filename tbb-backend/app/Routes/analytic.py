

from fastapi import APIRouter,Depends
from app.Core.utility import get_account_from_token
from app.Database.base import get_db, AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import selectinload
from app.Models.models import Position
from datetime import datetime,date
import pandas as pd
from sqlalchemy.orm import joinedload
from app.Models.models import PositionStatus
analytics_route =APIRouter()

@analytics_route.get("/performance_report")
async def performance_report(account:any=Depends(get_account_from_token),
                            db:AsyncSession =Depends(get_db)):
    query = select(Position).options(joinedload(Position.orders)).where(
         Position.account_id == account.account_id,
         Position.position_status==PositionStatus.COMPLETED
           ).order_by(Position.created_date.desc())
    result = await db.execute(query)
    positions = result.unique().scalars().all()
    if not positions:
        return {"message": "No positions found for the account."}
    


    return positions


@analytics_route.get("/performance_counts")
async def performance_counts(account:any=Depends(get_account_from_token),
                            db:AsyncSession =Depends(get_db)):
    pass