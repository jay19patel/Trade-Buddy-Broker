from app.Database.base import get_db
from sqlalchemy import select
from app.Models.models import Order, OrderTypes, LivePrice, OrderSide
from app.Core.utility import generate_unique_id

async def fetch_stop_orders(db):
    result = await db.execute(
        select(Order).where(
            Order.order_types == OrderTypes.STOPLIMIT,
            Order.stop_order_hit == False
        )
    )
    return result.scalars().all()

async def fetch_live_price_from_db(db, stock_isin):
    result = await db.execute(
        select(LivePrice).where(LivePrice.stock_isin == stock_isin)
    )
    return result.scalars().first()

async def create_exit_order(db, order, price):
    new_order_data = {
        "order_id": generate_unique_id("ORD"),
        "account_id": order.account_id,
        "position_id": order.position_id,
        "stock_symbol": order.stock_symbol,
        "order_types": order.order_types,
        "product_type": order.product_type,
        "stop_order_hit": True,
        "order_side": OrderSide.SELL if order.order_side == OrderSide.BUY else OrderSide.BUY,
        "trigger_price": price.price,
        "price": price.price,
        "quantity": order.quantity
    }
    new_order = Order(**new_order_data)
    db.add(new_order)

async def process_order(db, order, price):
    """Processes an order, updates it, and creates an exit order if conditions are met."""
    if (
        (order.order_side == OrderSide.BUY and price.price <= order.stoploss_trigger_price) or
        (order.order_side == OrderSide.SELL and price.price >= order.stoploss_trigger_price)
    ):
        order.stop_order_hit = True
        db.add(order)  # Mark the existing order for update
        await db.commit()  # Commit the update first
        print(f"Stop Order Hit for {order.stock_isin}")
        await create_exit_order(db, order, price)  # Create and add the exit order

async def main_auto_stoporder_exit_system():
    try:
        print("[ Auto Stop Order System Run]")
        async with get_db() as db:
            orders = await fetch_stop_orders(db)
            
            for order in orders:
                price = await fetch_live_price_from_db(db, order.stock_isin)
                if price:
                    await process_order(db, order, price)
            
            await db.commit()  # Commit changes to the database
    except Exception as e:
        print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main_auto_stoporder_exit_system())
