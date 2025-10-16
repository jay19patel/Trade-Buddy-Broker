# from app.delta_websoket import DeltaWebSocketClient
from app.config import config
import time

# def order_handle(message: dict) -> None:
#         print("-----------------[Order]-----------------")
#         results = message.get("result", [])
#         if not results:
#             print("No Orders found.")
#             return
#         print(f"Total Orders: {len(results)}")
#         for order in results:
#             print(order)
        

# def positions_handle(message: dict) -> None:
#     print("-----------------[Positions]-----------------")
#     results = message.get("result", [])
#     if not results:
#         print("No Positions found.")
#         return
#     print(f"Total Positions: {len(results)}")
#     for position in results:
#         print(position)



# subscriptions = {
#         "orders": ["all"],
#         "positions": ["all"]
#     }



# client = DeltaWebSocketClient(
#         websocket_url=config.websocket_url,
#         api_key=config.api_key,
#         api_secret=config.api_secret,
#         subscriptions=subscriptions,
#         orders_callback = order_handle ,
#         positions_callback = positions_handle,
#         ticker_callback = None,
#     )

# client.connect()




from app.delta_api import DeltaAPI
import time

delta_api = DeltaAPI(
    base_url='https://api.india.delta.exchange',
    api_key=config.api_key,
    api_secret=config.api_secret
)

print("\n=== Creating Entry + Stoploss/Target (with rollback) ===")

# Get current price from ticker
ticker_data = delta_api.get_ticker("VFYUSD")
current_price = float(ticker_data.get('mark_price'))
print(f"Symbol: {ticker_data.get('symbol')}")
print(f"Current Price: ${current_price}")
print(f"Mark Price: {ticker_data.get('mark_price')}")
print("Spot Price:", ticker_data.get('spot_price'))
print("Turnover Symbol:", ticker_data.get('turnover_symbol'))
print("Product ID:", ticker_data.get('product_id'))

# Set order side (change this to "buy" or "sell" as needed)
order_side = "buy"  # Change to "buy" or "sell"

# Calculate entry, stoploss, and target prices based on side
entry_price = current_price  # Entry at current price

if order_side == "buy":
    # For BUY: stoploss below entry, target above entry
    stop_loss_price = current_price * 0.995  # 0.5% below
    target_price = current_price * 1.01      # 1% above
    print(f"Order Type: BUY")
else:  # sell
    # For SELL: stoploss above entry, target below entry
    stop_loss_price = current_price * 1.005  # 0.5% above
    target_price = current_price * 0.99      # 1% below
    print(f"Order Type: SELL")

print(f"Entry Price: ${entry_price}")
print(f"Stop Loss: ${stop_loss_price}")
print(f"Target: ${target_price}")

# Create entry, then stoploss/target
print("\n=== Placing Entry, Stoploss and Target ===")
product_id = ticker_data.get('product_id')
if product_id:
    entry_resp = delta_api.create_entry(
        product_id=product_id,
        size=1,
        side=order_side,
        entry_price=entry_price,
        leverage=20
    )
    print("Entry order response:")
    print(entry_resp)



    time.sleep(3)

    entry_id = entry_resp.get('entry_order_id')
    st_resp = delta_api.create_stoploss_target(
        product_id=product_id,
        size=1,
        side=order_side,
        stoploss_price=stop_loss_price,
        target_price=target_price,
        entry_order_id=entry_id
    )
    print("Stoploss/Target response:")
    print(st_resp)



    time.sleep(10)

result = delta_api.emergency_exit()
print(f"Emergency exit response :")
print(result)

