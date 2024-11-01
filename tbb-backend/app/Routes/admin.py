
from fastapi import APIRouter,Depends,HTTPException,BackgroundTasks
from sqlalchemy import select,asc, desc,text,func
from typing import Dict, List,Optional
from app.Database.base import get_db, AsyncSession
from app.Schemas.admin import TicketCreate,ReplyBase,AccountList
from app.Models.model import TicketDB,ReplyDB
from  app.Core.security import generate_unique_id
from app.Core.tickit_email import email_send_for_ticket_replay
import asyncio


admin_route =APIRouter()

@admin_route.post("/tickets")
async def create_ticket(ticket: TicketCreate, db: AsyncSession = Depends(get_db)):
    db_ticket = TicketDB(**ticket.dict(), id= generate_unique_id("TKT"))
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket


@admin_route.get("/tickets")
async def get_tickets(
    search: Optional[str] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    filter_replied: Optional[str] = "all",
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TicketDB)

    # Add search filter
    if search:
        stmt = stmt.where(
            (TicketDB.id.ilike(f"%{search}%")) |
            (TicketDB.email.ilike(f"%{search}%")) |
            (TicketDB.title.ilike(f"%{search}%"))
        )

    # Add reply status filter
    if filter_replied != "all":
        stmt = stmt.where(TicketDB.replied == (filter_replied == "replied"))

    # Sort the query
    if sort_order.lower() == "desc":
        stmt = stmt.order_by(desc(getattr(TicketDB, sort_by)))
    else:
        stmt = stmt.order_by(asc(getattr(TicketDB, sort_by)))

    # Execute the statement
    result = await db.execute(stmt)
    tickets = result.scalars().all()

    return tickets
from sqlalchemy.orm import selectinload

@admin_route.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    # Query the ticket and eagerly load its replies
    stmt = (
        select(TicketDB)
        .where(TicketDB.id == ticket_id)
        .options(selectinload(TicketDB.replies))  # Eagerly load the replies
    )
    result = await db.execute(stmt)
    db_ticket = result.scalar_one_or_none()

    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return db_ticket

@admin_route.post("/tickets/{ticket_id}/reply")
async def reply_to_ticket(ticket_id: str, reply: ReplyBase, background_tasks: BackgroundTasks,db: AsyncSession = Depends(get_db)):
    # Fetch the ticket first
    stmt = select(TicketDB).where(TicketDB.id == ticket_id)
    result = await db.execute(stmt)
    db_ticket = result.scalar_one_or_none()

    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Create new reply object
    new_reply = ReplyDB(message =reply.message, ticket_id=ticket_id)
    data = {
        "ticket_id":db_ticket.id,
        "ticket_subject":db_ticket.title,
        "ticket_message":db_ticket.message,
        "ticket_reply":reply.message
    }
    loop = asyncio.get_event_loop()                  
    background_tasks.add_task(lambda: loop.create_task(email_send_for_ticket_replay([db_ticket.email],data)))
    
    # Add the reply to the database session and update the ticket's replied status
    db.add(new_reply)
    db_ticket.replied = True

    # Commit changes
    await db.commit()
    await db.refresh(db_ticket)
    await db.refresh(new_reply)
    return {"ticket": db_ticket, "new_reply": new_reply}


@admin_route.get("/accounts")
async def get_accounts(
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    sortBy: str = "full_name",
    sortOrder: str = "asc",
    search: Optional[str] = None
):
    try:
        query = """
        SELECT 
            a.account_id, 
            a.full_name,
            a.balance,
            a.description,
            a.created_datetime,
            a.is_activate,
            COALESCE(SUM(CASE WHEN t.transaction_type = 'DEPOSIT' THEN t.transaction_amount ELSE 0 END), 0) AS total_deposit,
            COALESCE(SUM(CASE WHEN t.transaction_type = 'WITHDRAW' THEN t.transaction_amount ELSE 0 END), 0) AS total_withdrawal,
            COALESCE(SUM(CASE WHEN t.transaction_type = 'DEPOSIT' THEN t.transaction_amount ELSE 0 END), 0) - 
            COALESCE(SUM(CASE WHEN t.transaction_type = 'WITHDRAW' THEN t.transaction_amount ELSE 0 END), 0) AS total_amount,
            (SELECT COUNT(*) FROM orders o WHERE o.account_id = a.account_id) AS total_trades,
            (SELECT COUNT(*) FROM orders o WHERE o.account_id = a.account_id AND o.order_side = 'BUY') AS positive_trades,
            (SELECT COUNT(*) FROM orders o WHERE o.account_id = a.account_id AND o.order_side = 'SELL') AS negative_trades
        FROM accounts a
        LEFT JOIN transactions t ON a.account_id = t.account_id
        WHERE 1=1
        """

        params = {}

        # Add search condition if provided
        if search:
            query += " AND (a.account_id ILIKE :search OR a.full_name ILIKE :search)"
            params['search'] = f"%{search}%"

        # Add grouping
        query += " GROUP BY a.account_id, a.full_name, a.balance, a.description, a.created_datetime,a.is_activate"

        # Add sorting
        query += f" ORDER BY {sortBy} {sortOrder.upper()}"  # Sorting after grouping

        # Add pagination
        offset = (page - 1) * 10
        params['limit'] = 10
        params['offset'] = offset
        query += " LIMIT :limit OFFSET :offset"  # Pagination parameters

        # Execute the query
        result = await db.execute(text(query), params)
        accounts = result.mappings().all()

        count_query = "SELECT COUNT(*) FROM accounts"
        if search:
            count_query += " WHERE (account_id ILIKE :search OR full_name ILIKE :search OR email_id ILIKE :search)"
        total_count_result = await db.execute(text(count_query), {'search': f"%{search}%"})
        total_count = (total_count_result.first())[0]
        total_pages = -(-total_count // 10)
        return AccountList(accounts=accounts, totalPages=total_pages)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))