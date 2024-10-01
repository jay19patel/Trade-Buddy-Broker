
from fastapi import APIRouter, Depends, HTTPException,Request,status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func,or_
from datetime import date
from typing import Optional
from datetime import date
from sqlalchemy.orm import joinedload
# APP
from app.Models.model import Order, Position, Account,PositionStatus,OrderSide,OrderTypes,CreateBy
from app.Database.base import get_db
from app.Core.security import generate_unique_id,get_account_from_token
from app.Schemas.order_schema import *
from app.Models.model import OrderTypes
from app.Core.responseBytb import TBException,TBResponse
order_route = APIRouter()

@order_route.post("/new_order/")
async def create_new_order(
    request: CreateNewOrder,
    account: Account = Depends(get_account_from_token), 
    db: AsyncSession = Depends(get_db) 
    )->TBResponse:
    """
    New Order Creation:
    - Creates a new position for the stock if it's a buy order.
    - Deducts order margin from the account balance.
    - Position and order are linked using `position_id`.
    """
    try:
        order_margin = request.quantity * request.price
        position_id = generate_unique_id("TRD")

        position_data = {
            "position_id": position_id,
            "account_id": account.account_id,
            "stock_symbol": request.stock_symbol,
            "stock_type": request.stock_type,
            "created_by": request.created_by,
            "stoploss_price":request.stoploss_price,
            "target_price":request.target_price
        }
        create_order = {
            "order_id": generate_unique_id("ORD"),
            "account_id": account.account_id,
            "position_id": position_id,
            "stock_symbol": request.stock_symbol,
            "order_types": OrderTypes.NewOrder,
            "order_side": request.order_side,
            "product_type": "CNC",
            "stop_order_hit": None,
            "stop_order_activate":True,
            "price": request.price,
            "stoploss_price": request.stoploss_price,
            "target_price": request.target_price,
            "quantity": request.quantity,
            "created_by": request.created_by
        }
        if order_margin > account.balance:
                raise Exception("Insufficient balance to place the order")

        if request.order_side == OrderSide.BUY:
            position_data.update({
                "buy_average": request.price,
                "buy_quantity": request.quantity,
                "buy_margin": order_margin,
                "position_side" :OrderSide.BUY
            })
        elif request.order_side == OrderSide.SELL:
            position_data.update({
                "sell_average": request.price,
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


        msg = f"New position created for {position_id} with {request.quantity} Quantity"
        return TBResponse(
            message=msg,
            payload= {
                "account": account.account_id,
                "order": order.order_id,
                "position": position.position_id
            }
        )
    except Exception as e :
        db.rollback()
        raise TBException(
            message=str(e),
            resolution=" An error occurred during creating order Try Again",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@order_route.post("/stoploss_order/")
async def create_stoploss_order(
    request: CreateStoplossOrder,
    account: Account = Depends(get_account_from_token), 
    db: AsyncSession = Depends(get_db) 
)->TBResponse:
    """
    Stop-Loss Order:
    - If the position exists, a stop-loss order is created or updated.
    - Updates stop-loss prices and refreshes the order details.
    """
    try:
        position = await db.scalar(select(Position).where(
            Position.position_id == request.position_id,
            Position.position_status == PositionStatus.PENDING
        ))


        if not position:
            raise Exception("Position not found")
        


        stop_order = await db.scalar(select(Order).where(
            Order.position_id == position.position_id,
            or_(
                Order.order_types == OrderTypes.StopLossOrder,
                Order.order_types == OrderTypes.NewOrder
            ),
            Order.stop_order_hit == False,
            Order.stop_order_activate == True
        ))

        position.target_price = request.target_price
        position.stoploss_price = request.stoploss_price

        if stop_order:
            stop_order.stop_order_activate = False

        create_stoploss_order = {
            "order_id": generate_unique_id("ORD"),
            "account_id": account.account_id,
            "position_id": position.position_id,
            "stock_symbol": position.stock_symbol,
            "order_types": OrderTypes.StopLossOrder,
            "product_type": position.product_type,
            "stoploss_price": request.stoploss_price,
            "target_price": request.target_price,
            "quantity": request.quantity,
            "created_by": request.created_by
        }
        order = Order(**create_stoploss_order)

        # Add new stop-loss order to session
        db.add_all([order,position])
        if stop_order:
            db.add(stop_order)    
        await db.commit()
        await db.refresh(order)
        await db.refresh(position)
        if stop_order:
            await db.refresh(stop_order)

        msg = "New Stop-loss Order Created" if not stop_order else "Stop-loss Order Updated"

        return TBResponse(
            message=msg,
            payload= {
                "account": account.account_id,
                "order": order.order_id,
                "position": position.position_id
            }
        )
    except Exception as e:
        db.rollback()
        raise TBException(
            message=str(e),
            resolution="try again",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@order_route.post("/update_quantity_order/")
async def update_quantity_order(
    request: UpdateQuantityOrder,
    account: Account = Depends(get_account_from_token), 
    db: AsyncSession = Depends(get_db)
) -> TBResponse:
    """
    Quantity Update Order:
    - Adds quantity to an existing position.
    - Updates the position's average price and margin accordingly.
    - Creates a new order.
    """
    try:
        # Fetch the position based on position_id and status
        position = await db.scalar(select(Position).where(
            Position.position_id == request.position_id,
            Position.position_status == PositionStatus.PENDING
        ))

        if position is None:
            raise Exception("Position not found!")

        if (request.order_side != position.position_side) and (request.quantity > abs(position.buy_quantity-position.sell_quantity)):
            raise Exception("Quantity not allow try again with another quantity")
        order_margin = request.quantity * request.price

        # Check for sufficient balance
        if order_margin > account.balance and position.position_side == request.order_side:
            raise Exception("Insufficient balance to place the order")

        # Update Position
        if request.order_side == OrderSide.BUY:
            position.buy_quantity += request.quantity
            position.buy_margin += order_margin
            position.buy_average = round((
                (position.buy_average * (position.buy_quantity - request.quantity) + request.price * request.quantity) /
                position.buy_quantity
            ), 2)

        elif request.order_side == OrderSide.SELL:
            position.sell_quantity += request.quantity
            position.sell_margin += order_margin
            position.sell_average = round((
                (position.sell_average * (position.sell_quantity - request.quantity) + request.price * request.quantity) /
                position.sell_quantity
            ), 2)

        # Update PnL if position side changes
        if position.position_side != request.order_side:
            position.pnl_total = round(
                (abs(position.buy_average - position.sell_average)) *
                (abs((position.buy_quantity + position.sell_quantity) / 2)), 2
            )

        # Update Account Balance
        account.balance += -order_margin if position.position_side == request.order_side else order_margin

        # Check if it's a full exit
        if position.buy_quantity == position.sell_quantity and position.position_status == PositionStatus.PENDING:
            pnl = (position.sell_average - position.buy_average) * position.sell_quantity
            position.pnl_total += pnl
            position.position_status = PositionStatus.COMPLETED
            msg = f"Position fully exited, PnL calculated: {pnl}"
            order_type = OrderTypes.ExitOrder
        else:
            msg = f"Quantity added to {request.order_side} position"
            order_type = OrderTypes.UpdateQtyOrder

        # Create a new order
        qty_update_order = {
            "order_id": generate_unique_id("ORD"),
            "account_id": account.account_id,
            "position_id": position.position_id,
            "stock_symbol": position.stock_symbol,
            "order_types": order_type,
            "order_side": request.order_side,
            "product_type": "CNC",
            "stop_order_hit": None,
            "price": request.price,
            "quantity": request.quantity,
            "created_by": request.created_by
        }

        order = Order(**qty_update_order)
        db.add_all([position, order, account])
        await db.commit()
        await db.refresh(position)
        await db.refresh(order)
        await db.refresh(account)

        return TBResponse(
            message=msg,
            payload={
                "account": account.account_id,
                "order": order.order_id,
                "position": position.position_id
            }
        )
    except Exception as e:
        await db.rollback()
        raise TBException(
            message=str(e),
            resolution="An error occurred during creating order. Try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    
@order_route.post("/create_exit_all_order/") 
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
    try:
        position = await db.scalar(select(Position).where(
                Position.position_id == request.position_id,
                Position.position_status == PositionStatus.PENDING
            ))
        if position is None:
             raise Exception("Position is not valid")
        
        sell_qty = (abs(position.buy_quantity-position.sell_quantity))
        sell_order = {
                "order_id": generate_unique_id("ORD"),
                "account_id": account.account_id,
                "position_id": position.position_id,
                "stock_symbol": position.stock_symbol,
                "order_types": OrderTypes.ExitOrder,
                "order_side":  OrderSide.SELL if position.position_side ==OrderSide.BUY else OrderSide.BUY,
                "product_type": position.product_type,
                "stop_order_hit": True,
                "price": request.price,
                "quantity": sell_qty,
                "created_by": request.created_by
            }
        order_margin = sell_qty * request.price
        
        if position.position_side == OrderSide.BUY:
                position.sell_quantity += sell_qty
                position.sell_margin += order_margin
                position.sell_average = (
                    (position.sell_average * (position.sell_quantity - sell_qty) + request.price * sell_qty) /
                    position.sell_quantity
                )
        elif position.position_side == OrderSide.SELL:
            position.buy_quantity += sell_qty
            position.buy_margin += order_margin
            position.buy_average = (
                (position.buy_average * (position.buy_quantity -sell_qty) + request.price *sell_qty) /
                position.buy_quantity
            )

        if position.buy_quantity == position.sell_quantity and position.position_status == PositionStatus.PENDING:
            pnl = (position.sell_average - position.buy_average) * position.sell_quantity
            position.pnl_total += pnl
            position.position_status = PositionStatus.COMPLETED
            msg = f"Position fully exited, PnL calculated: {pnl}"
        else:
            msg = "Exit order executed"

        account.balance += order_margin
        order = Order(**sell_order)
        db.add_all([position, order,account])
        await db.commit()
        await db.refresh(position)
        await db.refresh(order)
        await db.refresh(account)

        return TBResponse(
            message=msg,
            payload= {
                "account": account.account_id,
                "order": order.order_id,
                "position": position.position_id
            }
        )
    except Exception as e:
        await db.rollback()
        raise TBException(
            message=str(e),
            resolution="try again",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@order_route.get("/positions")
async def get_positions(account: Account = Depends(get_account_from_token),
                        db: AsyncSession = Depends(get_db)):
    try:
        query = select(Position).options(joinedload(Position.orders)).where(Position.account_id == account.account_id,
                or_(Position.position_status == PositionStatus.PENDING,
                    func.date(Position.created_date) == date.today())
                ).order_by(Position.created_date.desc())
        result = await db.execute(query)
        positions = result.unique().scalars().all()
        
        for position in positions:
            position.orders.sort(key=lambda x: x.order_datetime, reverse=True)

        total_pnl_result = await db.execute(select(func.sum(Position.pnl_total)).where(Position.account_id == account.account_id))  
        
        overview = {
            "total_positions": len(positions),
            "open_positions": sum(1 for p in positions if p.position_status == PositionStatus.PENDING),
            "closed_positions": sum(1 for p in positions if p.position_status == PositionStatus.COMPLETED),
            "pnl_todays": round(sum(p.pnl_total for p in positions),2),
            "positive_pnl_count": sum(1 for p in positions if p.pnl_total > 0),
            "negative_pnl_count": sum(1 for p in positions if p.pnl_total < 0),
            "balance":round(account.balance,2),
            "invested_amount":round(sum(abs(p.buy_margin-p.sell_margin)  for p in positions if p.position_status == PositionStatus.PENDING),2),
            "pnl_total":round(total_pnl_result.scalar(),2) or 0 }
        return {"positions":positions,"overview":overview}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Failed to retrieve data"}
    



@order_route.get("/all_positions")
async def get_single_position(
    account: Account = Depends(get_account_from_token),
    db: AsyncSession = Depends(get_db)):
    query = select(Position).options(joinedload(Position.orders)).where(
         Position.account_id == account.account_id,
         Position.position_status==PositionStatus.COMPLETED
           ).order_by(Position.created_date.desc())
    result = await db.execute(query)
    positions = result.unique().scalars().all()
    for position in positions:
        position.orders.sort(key=lambda x: x.order_datetime, reverse=True)

    return positions