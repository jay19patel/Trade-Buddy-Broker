from app.delta import DeltaWebSocketClient
from app.config import config


def order_handle(message: dict) -> None:
        print("-----------------[Order]-----------------")
        results = message.get("result", [])
        if not results:
            print("No Orders found.")
            return
        print(f"Total Orders: {len(results)}")
        for order in results:
            print(order)
        

def positions_handle(message: dict) -> None:
    print("-----------------[Positions]-----------------")
    results = message.get("result", [])
    if not results:
        print("No Positions found.")
        return
    print(f"Total Positions: {len(results)}")
    for position in results:
        print(position)



subscriptions = {
        "orders": ["all"],
        "positions": ["all"]
    }



client = DeltaWebSocketClient(
        websocket_url=config.websocket_url,
        api_key=config.api_key,
        api_secret=config.api_secret,
        subscriptions=subscriptions,
        orders_callback = order_handle ,
        positions_callback = positions_handle,
        ticker_callback = None,
    )

client.connect()