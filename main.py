# from app.delta_websoket import DeltaWebSocketClient
from app.config import config


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

delta_api = DeltaAPI(
    base_url='https://api.india.delta.exchange',
    api_key=config.api_key,
    api_secret=config.api_secret
)

# Simple API calls without Pydantic models - Much faster execution!
print("=== Product ID 174 Details ===")
product_details = delta_api.get_product(174)
print(f"Symbol: {product_details.get('symbol', 'N/A')}")
print(f"Description: {product_details.get('description', 'N/A')}")

print("\n=== Ticker Data ===")
ticker_data = delta_api.get_ticker("VFYUSD")
print(ticker_data)



# from app.delta_schema import GetTickerRequest
# get_ticker_request = GetTickerRequest(symbol=".DEXBTUSD")
# ticker = delta_api.get_ticker(get_ticker_request)
# print(ticker)


# assets = delta_api.get_assets()
# print(assets)
# for i in assets:
#     print(i)
#     print('------------------\n')

# balance_request = GetBalancesRequest(asset_id=1)
# balances = delta_api.get_balances(balance_request)
# print(balances)