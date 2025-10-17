# # from app.delta_websoket import DeltaWebSocketClient
# from app.config import config
# import time

# # def order_handle(message: dict) -> None:
# #         print("-----------------[Order]-----------------")
# #         results = message.get("result", [])
# #         if not results:
# #             print("No Orders found.")
# #             return
# #         print(f"Total Orders: {len(results)}")
# #         for order in results:
# #             print(order)
        

# # def positions_handle(message: dict) -> None:
# #     print("-----------------[Positions]-----------------")
# #     results = message.get("result", [])
# #     if not results:
# #         print("No Positions found.")
# #         return
# #     print(f"Total Positions: {len(results)}")
# #     for position in results:
# #         print(position)



# # subscriptions = {
# #         "orders": ["all"],
# #         "positions": ["all"]
# #     }



# # client = DeltaWebSocketClient(
# #         websocket_url=config.websocket_url,
# #         api_key=config.api_key,
# #         api_secret=config.api_secret,
# #         subscriptions=subscriptions,
# #         orders_callback = order_handle ,
# #         positions_callback = positions_handle,
# #         ticker_callback = None,
# #     )

# # client.connect()




from app.delta_api import DeltaAPI
import time
from app.config import config

delta_api = DeltaAPI(
    base_url='https://api.india.delta.exchange',
    api_key=config.api_key,
    api_secret=config.api_secret
)


data = delta_api.emergency_exit()
print(data)


# print("\n=== Creating Entry + Stoploss/Target (with rollback) ===")

# Get account balance first
# print("\n=== Account Balance ===")
# try:
#     balance = delta_api.get_balance()
#     print(f"Balance Response: {balance}")
# except Exception as e:
#     print(f"Error fetching balance: {e}")

# # Get current price from ticker
# ticker_data = delta_api.get_ticker("VFYUSD")
# current_price = float(ticker_data.get('mark_price'))
# print(f"Symbol: {ticker_data.get('symbol')}")
# print(f"Current Price: ${current_price}")
# print(f"Mark Price: {ticker_data.get('mark_price')}")
# print("Spot Price:", ticker_data.get('spot_price'))
# print("Turnover Symbol:", ticker_data.get('turnover_symbol'))
# print("Product ID:", ticker_data.get('product_id'))

# # Set order side (change this to "buy" or "sell" as needed)
# order_side = "buy"  # Change to "buy" or "sell"

# # # Calculate entry, stoploss, and target prices based on side
# entry_price = current_price  # Entry at current price

# if order_side == "buy":
#     # For BUY: stoploss 1% below entry, target 1% above entry
#     stop_loss_price = current_price * 0.99
#     target_price = current_price * 1.01
#     print(f"Order Type: BUY")
# else:  # sell
#     # For SELL: stoploss 1% above entry, target 1% below entry
#     stop_loss_price = current_price * 1.01
#     target_price = current_price * 0.99
#     print(f"Order Type: SELL")

# print(f"Entry Price: ${entry_price}")
# print(f"Stop Loss: ${stop_loss_price}")
# print(f"Target: ${target_price}")

# # Create entry, then stoploss/target
# # print("\n=== Placing Entry, Stoploss and Target ===")
# product_id = ticker_data.get('product_id')
# if product_id:
#     entry_resp = delta_api.create_entry(
#         product_id=product_id,
#         size=1,
#         side=order_side,
#         entry_price=entry_price,
#         leverage=20
#     )

#     time.sleep(15)
#     st_resp = delta_api.create_stoploss_target(
#         product_id=product_id,
#         symbol=ticker_data.get('symbol'),
#         stoploss_price=stop_loss_price,
#         target_price=target_price,
#     )
#     print("Stoploss/Target response:")
#     print(st_resp)







# ----------------------------- Redis Subscriber ----------------------------- #


# from app.event import RedisSubscriber
# from app.delta_api import DeltaAPI
# from app.config import config
# from typing import Callable, Optional, Dict, Any
# import json


# def main():
#     """
#     Example usage of RedisSubscriber class
#     """
#     def my_callback(channel: str, data: Dict[str, Any],**kwargs) -> None:
#         try:
#        # data is already parsed JSON, no need to parse again
#             res_data = []
#             result = data.get("data", {}).get("results", [])
#             if result and len(result) > 0:
#                 for symbol_data in result:
#                     symbol = symbol_data.get("symbol")
#                     strategies = symbol_data.get("strategies", [])  
#                     print(f"Symbol: {symbol} Strategies: {strategies}")
#                     for strategy in strategies:
#                         signal_type = strategy.get("signal_type")
#                         success = strategy.get("sucess", False)  # Note: keeping the typo as it appears in the data
#                         if signal_type != "HOLD" and success:
#                             res_data.append(strategy)
#                         else:
#                             print(f"SKIPPING HOLD SIGNAL for {symbol} - {strategy.get('strategy_name')}")
#             res_data = sorted(res_data, key=lambda x: x.get("confidence"), reverse=True)
#             print(f"Res data: {res_data}")
#             # [{'strategy_name': 'EMA Crossover Strategy', 'symbol': 'ETH-USD', 'signal_type': 'BUY', 'confidence': 0.9, 'execution_time': 0.2605619430541992, 'timestamp': '2025-10-16T17:26:26.215781+00:00', 'price': 3500.25, 'created_at': '2025-10-16 17:27:27.052658+00:00', '_id': '68f12affa35bc12cbe3ca58c', 'sucess': True}, {'strategy_name': 'Bollinger Bands Mean Reversion Strategy', 'symbol': 'BTC-USD', 'signal_type': 'BUY', 'confidence': 0.85, 'execution_time': 0.2602965831756592, 'timestamp': '2025-10-16T17:26:26.215781+00:00', 'price': 67500.5, 'created_at': '2025-10-16 17:27:27.047146+00:00', '_id': '68f12aff8b680056ab3ca58a', 'sucess': True}, {'strategy_name': 'MACD Convergence Divergence Strategy', 'symbol': 'BTC-USD', 'signal_type': 'SELL', 'confidence': 0.75, 'execution_time': 0.36953139305114746, 'timestamp': '2025-10-16T17:26:26.215781+00:00', 'price': 67500.5, 'created_at': '2025-10-16 17:27:27.157807+00:00', '_id': '68f12affcc5b501c1c3ca58b', 'sucess': True}]
#             # return res_data
#         except Exception as e:
#             print(f"Error: {e}")

#     delta_api = DeltaAPI(
#         base_url='https://api.india.delta.exchange',
#         api_key=config.api_key,
#         api_secret=config.api_secret
#     )
#     # Create subscriber instance
#     subscriber = RedisSubscriber()

    
    
#     try:
#         # Connect to Redis (automatically subscribes to channel)
#         subscriber.connect()

#         subscriber.add_callback_arguments(delta=delta_api)
        
#         # Set callback function
#         subscriber.set_callback(my_callback)
        
#         # Start listening
#         subscriber.start_listening()
        
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         subscriber.stop_listening()


# if __name__ == "__main__":
#     main()





