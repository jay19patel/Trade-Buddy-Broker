
from fastapi import APIRouter,Path, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func,or_
from datetime import date
from app.Models.models import Order, Position, Account,PositionStatus,OrderSide,OrderTypes,CreateBy
from app.Database.base import get_db
from app.Core.utility import get_account_from_token, generate_unique_id
from app.Schemas.Order import *
from datetime import date
from app.Models.models import OrderTypes
from typing import Optional
order_route = APIRouter()


@order_route.post("/new_order/")
async def create_new_order(
    request: CreateNewOrder,
    account: Account = Depends(get_account_from_token), 
    db: AsyncSession = Depends(get_db) 
    ):
    """
    New Order Creation:
    - Creates a new position for the stock if it's a buy order.
    - Deducts order margin from the account balance.
    - Position and order are linked using `position_id`.
    """
    order_margin = request.quantity * request.limit_price
    position_id = generate_unique_id("TRD")

    position_data = {
        "position_id": position_id,
        "account_id": account.account_id,
        "stock_symbol": request.stock_symbol,
        "stock_isin": request.stock_isin,
        "current_price": request.limit_price,
        "created_by": request.created_by
    }

    create_order = {
        "order_id": generate_unique_id("ORD"),
        "account_id": account.account_id,
        "position_id": position_id,
        "stock_isin": request.stock_isin,
        "stock_symbol": request.stock_symbol,
        "order_types": OrderTypes.NewOrder,
        "order_side": request.order_side,
        "product_type": "CNC",
        "stop_order_hit": None,
        "stop_order_activate":True,
        "trigger_price": request.trigger_price,
        "limit_price": request.limit_price,
        "stoploss_limit_price": request.stoploss_limit_price,
        "stoploss_trigger_price": request.stoploss_trigger_price,
        "target_limit_price": request.target_limit_price,
        "target_trigger_price": request.target_trigger_price,
        "quantity": request.quantity,
        "created_by": request.created_by
    }
    if request.order_side == OrderSide.BUY and order_margin > account.balance:
            raise HTTPException(status_code=400, detail="Insufficient balance to place the order")

    if request.order_side == OrderSide.BUY:
        position_data.update({
            "buy_average": request.limit_price,
            "buy_quantity": request.quantity,
            "buy_margin": order_margin,
            "position_side" :OrderSide.BUY
        })
    elif request.order_side == OrderSide.SELL:
        position_data.update({
            "sell_average": request.limit_price,
            "sell_quantity": request.quantity,
            "sell_margin": order_margin,
            "position_side" :OrderSide.SELL
        })

    account.balance -= order_margin
    position = Position(**position_data)
    order = Order(**create_order)
    db.add_all([account, position, order])
    await db.commit()
    await db.refresh(order)
    await db.refresh(position)
    await db.refresh(account)

    msg = f"New position created for {position_id}"
    return {
        "status": "success",
        "message": msg,
        "payload": {
            "account": account.account_id,
            "order": order.order_id,
            "position": position.position_id
        }
    }


@order_route.post("/stoploss_order/")
async def create_stoploss_order(
    request: CreateStoplossOrder,
    account: Account = Depends(get_account_from_token), 
    db: AsyncSession = Depends(get_db) 
):
    """
    Stop-Loss Order:
    - If the position exists, a stop-loss order is created or updated.
    - Updates stop-loss prices and refreshes the order details.
    """
    position = await db.scalar(select(Position).where(
        Position.position_id == request.position_id,
        Position.position_status == PositionStatus.PENDING
    ))

    if not position:
        return {"status": "error", "message": "Position not found or not pending."}

    stop_order = await db.scalar(select(Order).where(
        Order.position_id == position.position_id,
        or_(
            Order.order_types == OrderTypes.StopLossOrder,
            Order.order_types == OrderTypes.NewOrder
        ),
        Order.stop_order_hit == False,
        Order.stop_order_activate == True
    ))

    print("stop_order:", stop_order)

    if stop_order:
        stop_order.stop_order_activate = False

    create_stoploss_order = {
        "order_id": generate_unique_id("ORD"),
        "account_id": account.account_id,
        "position_id": position.position_id,
        "stock_isin": position.stock_isin,
        "stock_symbol": position.stock_symbol,
        "order_types": OrderTypes.StopLossOrder,
        "product_type": position.product_type,
        "stoploss_limit_price": request.stoploss_limit_price,
        "stoploss_trigger_price": request.stoploss_trigger_price,
        "target_limit_price": request.target_limit_price,
        "target_trigger_price": request.target_trigger_price,
        "quantity": request.quantity,
        "created_by": request.created_by
    }
    order = Order(**create_stoploss_order)

    # Add new stop-loss order to session
    db.add(order)
    if stop_order:
        db.add(stop_order)    
    await db.commit()
    await db.refresh(order)
    if stop_order:
        await db.refresh(stop_order)

    msg = "New Stop-loss Order Created" if not stop_order else "Stop-loss Order Updated"

    return {
        "status": "success",
        "message": msg,
        "payload": {
            "account": account.account_id,
            "order": order.order_id,
            "position": position.position_id
        }
    }

    
@order_route.post("/quantity_add_order/")
async def add_quantity_in_position(
    request: AddQuantityOrder,
    account: Account = Depends(get_account_from_token), 
    db: AsyncSession = Depends(get_db) 
    ):
    """
    Quantity Add Order:
    - Adds quantity to an existing position.
    - Updates the position's average price and margin accordingly.
    - create new order 
    """
    position = await db.scalar(select(Position).where(
            Position.position_id == request.position_id,
            Position.position_status == PositionStatus.PENDING
        ))
    order_margin = request.quantity * request.limit_price
    
    if request.order_side == OrderSide.BUY:
            position.buy_quantity += request.quantity
            position.buy_margin += order_margin
            position.buy_average = (
                (position.buy_average * (position.buy_quantity - request.quantity) + request.limit_price * request.quantity) /
                position.buy_quantity
            )
    elif request.order_side == OrderSide.SELL:
            position.sell_quantity += request.quantity
            position.sell_margin += order_margin
            position.sell_average = (
                (position.sell_average * (position.sell_quantity - request.quantity) + request.limit_price * request.quantity) /
                position.sell_quantity
            )
    qty_add_order = {
            "order_id": generate_unique_id("ORD"),
            "account_id": account.account_id,
            "position_id": position.position_id,
            "stock_isin": position.stock_isin,
            "stock_symbol": position.stock_symbol,
            "order_types": OrderTypes.QtyAddOrder,
            "order_side": request.order_side,
            "product_type": "CNC",
            "stop_order_hit": None,
            "limit_price": request.limit_price,
            "quantity": request.quantity,
            "created_by": request.created_by
        }

    order = Order(**qty_add_order)
    db.add_all([position, order])
    await db.commit()
    await db.refresh(position)
    await db.refresh(order)
    msg = f"Quantity added to {request.order_side} position"
    return {
        "status": "success",
        "message": msg,
        "payload": {
            "account": account.account_id,
            "order": order.order_id,
            "position": position.position_id
        }
    }
    
@order_route.post("/create_exit_order/") 
async def create_exit_order(
    request: CreateExitOrder,
    account: Account = Depends(get_account_from_token), 
    db: AsyncSession = Depends(get_db) 
    ):
    """
    Exit Order:
    - Updates the position's sell quantity and margins.
    - If fully exited, marks the position as completed and calculates the PnL.
    """
    position = await db.scalar(select(Position).where(
            Position.position_id == request.position_id,
            Position.position_status == PositionStatus.PENDING
        ))
    sell_order = {
            "order_id": generate_unique_id("ORD"),
            "account_id": account.account_id,
            "position_id": position.position_id,
            "stock_isin": position.stock_isin,
            "stock_symbol": position.stock_symbol,
            "order_types": OrderTypes.ExitOrder,
            "order_side":  OrderSide.SELL if request.order_side else OrderSide.BUY,
            "product_type": position.product_type,
            "stop_order_hit": True,
            "limit_price": request.limit_price,
            "quantity": request.quantity,
            "created_by": request.created_by
        }
    order_margin = request.quantity * request.limit_price
    
    if request.order_side == OrderSide.BUY:
            position.sell_quantity += request.quantity
            position.sell_margin += order_margin
            position.sell_average = (
                (position.sell_average * (position.sell_quantity - request.quantity) + request.limit_price * request.quantity) /
                position.sell_quantity
            )
    elif request.order_side == OrderSide.SELL:
        position.buy_quantity += request.quantity
        position.buy_margin += order_margin
        position.buy_average = (
            (position.buy_average * (position.buy_quantity - request.quantity) + request.limit_price * request.quantity) /
            position.buy_quantity
        )

    if position.buy_quantity == position.sell_quantity and position.position_status == PositionStatus.PENDING:
        pnl = (position.sell_average - position.buy_average) * position.sell_quantity
        position.pnl_total += pnl
        position.position_status = PositionStatus.COMPLETED
        msg = f"Position fully exited, PnL calculated: {pnl}"
    else:
        msg = "Exit order executed"

    order = Order(**sell_order)
    db.add_all([position, order])
    await db.commit()
    await db.refresh(position)
    await db.refresh(order)

    return {
        "status": "success",
        "message": msg,
        "payload": {
            "account": account.account_id,
            "order": order.order_id,
            "position": position.position_id
        }
    }
    

@order_route.get("/all_orders")
async def get_all_order(
            account: Account = Depends(get_account_from_token),
            db: AsyncSession = Depends(get_db)):
    
    query = select(Order).where(Order.account_id == account.account_id).order_by(Order.order_datetime.desc())
    data = await db.execute(query)
    return data.scalars().all()


@order_route.get("/all_orders/{position_id}")
async def get_all_order_for_position(
            position_id : str,
            account: Account = Depends(get_account_from_token),
            db: AsyncSession = Depends(get_db)):
    
    query = select(Order).where(Order.account_id == account.account_id,Order.position_id== position_id).order_by(Order.order_datetime.desc())
    data = await db.execute(query)
    return data.scalars().all()


@order_route.get("/open_orders")
async def get_open_order(
            account: Account = Depends(get_account_from_token),
            db: AsyncSession = Depends(get_db)):
    
    query = select(Order).where(Order.account_id == account.account_id
                                # ,Order.order_types == OrderTypes.StopLossOrder
                                ,Order.stop_order_hit == False
                                ,Order.stop_order_activate== True
                                ).order_by(Order.order_datetime.desc())
    data = await db.execute(query)
    return data.scalars().all()



@order_route.get("/position/{position_id}/")
async def get_single_position(
    position_id: str = None,
    account: Account = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)):

    query = select(Position).where(Position.account_id == account.account_id,
                                   Position.position_id == position_id).order_by(Position.created_date.desc())
    if position_id:
        query = query.where(
            Order.account_id == account.account_id,
            Order.position_id == position_id)
    data = await db.execute(query)
    return data.scalars().all()


from sqlalchemy.orm import joinedload
from sqlalchemy import desc

@order_route.get("/positions")
async def get_positions(trade_today: bool = False,
                        account: Account = Depends(get_account_from_token),
                        db: AsyncSession = Depends(get_db)):
    try:
        query = select(Position).options(
            joinedload(Position.orders)
        ).where(Position.account_id == account.account_id)

        if trade_today:
            current_date = date.today()
            query = query.where(
                func.date(Position.created_date) == current_date,
                Position.position_status == PositionStatus.PENDING
            ).order_by(Position.created_date.desc())

        result = await db.execute(query)
        positions = result.unique().scalars().all()
        for position in positions:
            position.orders.sort(key=lambda x: x.order_datetime, reverse=True)

        # Overview creation
        overview = {
            "total_positions": len(positions),
            "open_positions": sum(1 for p in positions if p.position_status == PositionStatus.PENDING),
            "closed_positions": sum(1 for p in positions if p.position_status == PositionStatus.COMPLETED),
            "pnl_realized": sum(p.pnl_total for p in positions if p.position_status == PositionStatus.COMPLETED),
            "pnl_unrealized": sum(p.pnl_total for p in positions if p.position_status != PositionStatus.COMPLETED),
            "pnl_total": sum(p.pnl_total for p in positions)
        }

        return {"data": positions, "overview": overview}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Failed to retrieve data"}


