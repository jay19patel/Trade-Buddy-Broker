from app.delta_websoket import DeltaWebSocketClient
from app.config import config
import time

def order_handle(orders: list) -> None:
    print("\n" + "="*80)
    print("                              ORDER UPDATE")
    print("="*80)

    if not orders:
        print("No Orders found.")
        print("="*80 + "\n")
        return

    for order in orders:
        action = order.get('action', 'N/A')
        print(f"\n🔔 Action: {action.upper()}")
        print("-" * 80)

        # Basic Order Info
        print(f"Order ID       : {order.get('id', 'N/A')}")
        print(f"Symbol         : {order.get('symbol', 'N/A')}")
        print(f"Side           : {order.get('side', 'N/A').upper()}")
        print(f"Order Type     : {order.get('order_type', 'N/A')}")
        print(f"State          : {order.get('state', 'N/A').upper()}")

        # Size & Pricing
        print(f"\nSize           : {order.get('size', 'N/A')}")
        print(f"Unfilled Size  : {order.get('unfilled_size', 'N/A')}")
        print(f"Filled Size    : {order.get('filled_size', 'N/A')}")
        print(f"Limit Price    : {order.get('limit_price', 'N/A')}")

        avg_fill_price = order.get('average_fill_price')
        if avg_fill_price:
            print(f"Avg Fill Price : {avg_fill_price}")

        # Commission & PnL
        commission = order.get('commission', '0')
        paid_commission = order.get('paid_commission', '0')
        print(f"\nCommission     : {commission}")
        print(f"Paid Commission: {paid_commission}")

        # Meta Data (PnL info for filled orders)
        meta_data = order.get('meta_data', {})
        if meta_data:
            pnl = meta_data.get('pnl')
            cashflow = meta_data.get('cashflow')
            entry_price = meta_data.get('entry_price')
            avg_exit_price = meta_data.get('avg_exit_price')
            roe = meta_data.get('roe')

            if pnl or cashflow:
                print(f"\n💰 Trade Details:")
                if entry_price:
                    print(f"Entry Price    : {entry_price}")
                if avg_exit_price:
                    print(f"Exit Price     : {avg_exit_price}")
                if pnl:
                    print(f"PnL            : {pnl}")
                if cashflow:
                    print(f"Cashflow       : {cashflow}")
                if roe:
                    print(f"ROE            : {float(roe):.2f}%")

        # Reason for state change
        reason = order.get('reason')
        if reason:
            print(f"\nReason         : {reason}")

        # Timestamps
        print(f"\nCreated At     : {order.get('created_at', 'N/A')}")
        print(f"Updated At     : {order.get('updated_at', 'N/A')}")

    print("="*80 + "\n")


def positions_handle(positions: list) -> None:
    print("\n" + "="*80)
    print("                           POSITION UPDATE")
    print("="*80)

    if not positions:
        print("No Positions found.")
        print("="*80 + "\n")
        return

    for position in positions:
        action = position.get('action', 'N/A')
        print(f"\n🔔 Action: {action.upper()}")
        print("-" * 80)

        # Basic Position Info
        print(f"Symbol         : {position.get('symbol', 'N/A')}")
        print(f"Size           : {position.get('size', 'N/A')}")

        # Pricing
        entry_price = position.get('entry_price', 'N/A')
        liquidation_price = position.get('liquidation_price', 'N/A')
        bankruptcy_price = position.get('bankruptcy_price', 'N/A')

        print(f"\nEntry Price    : {entry_price}")
        if liquidation_price:
            print(f"Liquidation    : {liquidation_price}")
        if bankruptcy_price:
            print(f"Bankruptcy     : {bankruptcy_price}")

        # Margin Info
        margin = position.get('margin', 'N/A')
        margin_mode = position.get('margin_mode', 'N/A')
        print(f"\nMargin         : {margin}")
        print(f"Margin Mode    : {margin_mode.upper()}")

        # PnL & Cashflow
        realized_pnl = position.get('realized_pnl', '0')
        realized_cashflow = position.get('realized_cashflow', '0')
        realized_funding = position.get('realized_funding', '0')
        commission = position.get('commission', '0')

        print(f"\n💰 Financial Summary:")
        print(f"Realized PnL   : {realized_pnl}")
        print(f"Cashflow       : {realized_cashflow}")
        print(f"Funding        : {realized_funding}")
        print(f"Commission     : {commission}")

        # Risk Info
        adl_level = position.get('adl_level')
        under_liquidation = position.get('under_liquidation', False)

        if adl_level or under_liquidation:
            print(f"\n⚠️  Risk Info:")
            if adl_level:
                print(f"ADL Level      : {adl_level}")
            print(f"Under Liq.     : {'YES ⚠️' if under_liquidation else 'NO'}")

    print("="*80 + "\n")


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