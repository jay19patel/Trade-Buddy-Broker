"""
Delta Exchange API Usage Examples (Simple Parameter Version)

Ye file dikhata hai kaise aap DeltaAPI class ko simple parameters ke saath
use kar sakte hain (no Pydantic models).
"""

from app.delta_api import DeltaAPI


def initialize_delta_api():
    """Initialize Delta API client"""

    # For Testnet India
    delta_api = DeltaAPI(
        base_url='https://cdn-ind.testnet.deltaex.org',
        api_key='your_api_key_here',
        api_secret='your_api_secret_here'
    )

    # For Production India (uncomment below)
    # delta_api = DeltaAPI(
    #     base_url='https://api.india.delta.exchange',
    #     api_key='your_api_key_here',
    #     api_secret='your_api_secret_here'
    # )

    return delta_api


def example_market_data():
    """Market Data Examples"""
    delta = initialize_delta_api()

    # 1. Get all assets
    print("=== Get Assets ===")
    assets = delta.get_assets()
    print(assets)

    # 2. Get specific product details
    print("\n=== Get Product Detail ===")
    product = delta.get_product(27)
    print(f"Product: {product}")
    print(f"Settling Asset: {product.get('settling_asset')}")

    # 3. Get ticker data
    print("\n=== Get Ticker ===")
    ticker = delta.get_ticker("BTCUSD")
    print(ticker)

    # 4. Get L2 orderbook
    print("\n=== Get L2 Orderbook ===")
    orderbook = delta.get_l2_orderbook(27)
    print(orderbook)


def example_order_operations():
    """Order Operations Examples"""
    delta = initialize_delta_api()

    # 1. Get live (open) orders
    print("=== Get Live Orders ===")
    live_orders = delta.get_live_orders()
    print(live_orders)

    # 2. Place a LIMIT order
    print("\n=== Place Limit Order ===")
    order_response = delta.place_order(
        product_id=27,
        size=10,
        side="buy",
        order_type="limit",
        limit_price="50000.5",
        reduce_only=False,
    )
    print(order_response)

    # 3. Place a MARKET order
    print("\n=== Place Market Order ===")
    order_response = delta.place_order(
        product_id=27,
        size=5,
        side="sell",
        order_type="market",
    )
    print(order_response)

    # 4. Place a STOP LOSS order
    print("\n=== Place Stop Loss Order ===")
    stop_response = delta.place_stop_order(
        product_id=27,
        size=10,
        side="sell",
        order_type="market",
        stop_price="48000.0",
        is_trailing_stop_loss=False,
    )
    print(stop_response)

    # 5. Place a TRAILING STOP LOSS order
    print("\n=== Place Trailing Stop Loss Order ===")
    trailing_response = delta.place_stop_order(
        product_id=27,
        size=10,
        side="sell",
        order_type="limit",
        trail_amount="500.0",
        limit_price="49000.0",
        is_trailing_stop_loss=True,
    )
    print(trailing_response)

    # 6. Cancel an order
    print("\n=== Cancel Order ===")
    cancel_response = delta.cancel_order(product_id=27, order_id=123456)
    print(cancel_response)

    # 7. Batch create orders (max 5)
    print("\n=== Batch Create Orders ===")
    batch_create_response = delta.batch_create_orders(
        product_id=27,
        orders=[
            {"size": 5, "side": "buy", "limit_price": "49000.0", "order_type": "limit"},
            {"size": 5, "side": "buy", "limit_price": "48500.0", "order_type": "limit"},
            {"size": 5, "side": "sell", "limit_price": "51000.0", "order_type": "limit"},
        ],
    )
    print(batch_create_response)

    # 8. Batch cancel orders (max 5)
    print("\n=== Batch Cancel Orders ===")
    batch_cancel_response = delta.batch_cancel_orders(
        product_id=27,
        order_ids=[123456, 123457, 123458],
    )
    print(batch_cancel_response)

    # 9. Get order history with pagination
    print("\n=== Get Order History ===")
    history = delta.get_order_history(query={"product_id": 27}, page_size=100)
    print(f"Orders: {history['result']}")

    # Get next page if available
    if history.get('meta', {}).get('after'):
        next_page = delta.get_order_history(
            query={"product_id": 27},
            page_size=100,
            after=history['meta']['after']
        )
        print(f"Next page orders: {next_page['result']}")

    # 10. Get fills (trade history)
    print("\n=== Get Fills ===")
    fills = delta.get_fills(query={"contract_types": "futures,interest_rate_swaps"}, page_size=50)
    print(fills)


def example_position_operations():
    """Position Operations Examples"""
    delta = initialize_delta_api()

    # 1. Get current position
    print("=== Get Position ===")
    position = delta.get_position(27)
    print(position)

    # 2. Change position margin
    print("\n=== Change Position Margin ===")
    margin_response = delta.change_position_margin(product_id=27, margin="1000.0")
    print(margin_response)

    # 3. Set leverage for new orders
    print("\n=== Set Leverage ===")
    leverage_response = delta.set_leverage(product_id=27, leverage="25")
    print(leverage_response)


def example_wallet_operations():
    """Wallet Operations Examples"""
    delta = initialize_delta_api()

    # Get wallet balances
    print("=== Get Wallet Balances ===")
    balances = delta.get_balances(1)
    print(balances)

def example_common_errors():
    """Examples showing common mistakes with simple parameter API"""

    print("=== Common Error Examples ===")

    # 1. LIMIT order without limit_price
    try:
        delta = initialize_delta_api()
        delta.place_order(product_id=27, size=1, side="buy", order_type="limit")
    except Exception as e:
        print(f"Expected error (missing limit_price): {e}")

    # 2. Unsupported order_type
    try:
        delta = initialize_delta_api()
        delta.place_order(product_id=27, size=1, side="buy", order_type="foo")
    except Exception as e:
        print(f"Expected error (bad order_type): {e}")


if __name__ == "__main__":
    print("Delta Exchange API Examples")
    print("=" * 50)

    # Uncomment the examples you want to run:

    # example_market_data()
    # example_order_operations()
    # example_position_operations()
    # example_wallet_operations()
    # example_common_errors()

    print("\nNote: Make sure to set your API key and secret before running!")
