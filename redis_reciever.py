
# ----------------------------- Redis Subscriber ----------------------------- #


from app.event import RedisSubscriber
from app.delta_api import DeltaAPI
from app.config import config
from typing import Callable, Optional, Dict, Any
import json
from app.trade_calculator import TradeCalculator

def main():
    """
    Example usage of RedisSubscriber class
    """
    def my_callback(channel: str, data: Dict[str, Any], **kwargs) -> None:
        try:
            # data is already parsed JSON
            delta_api: DeltaAPI = kwargs.get("delta")
            results = data.get("data", {}).get("results", [])
            res_data = []

            if not results:
                print("No results found in data.")
                return

            for symbol_data in results:
                symbol = symbol_data.get("symbol")
                strategies = symbol_data.get("strategies", [])

                if not strategies:
                    print(f"No strategies for {symbol}")
                    continue

                # ✅ Pick the strategy with the highest confidence
                best_strategy = max(strategies, key=lambda s: s.get("confidence", 0.0))

                signal_type = best_strategy.get("signal_type")
                success = best_strategy.get("sucess", True)  # Keep typo as in source

                print(f"Symbol: {symbol} | Best Strategy: {best_strategy.get('strategy_name')} | Confidence: {best_strategy.get('confidence')} | Signal: {signal_type}")

                # Skip HOLD or unsuccessful signals
                if signal_type == "HOLD" or not success:
                    print(f"Skipping HOLD or failed strategy for {symbol}")
                    continue

                res_data.append(best_strategy)

            # ✅ Sort final selected strategies by confidence
            res_data = sorted(res_data, key=lambda x: x.get("confidence", 0), reverse=True)

            print(f"Filtered Result Data (Highest per symbol): {res_data}")

            # === Trading Execution ===
            for trade in res_data:
                symbol = trade.get("symbol")
                signal_type = trade.get("signal_type")

                ticker_data = delta_api.get_ticker(symbol)
                product_id = ticker_data.get("product_id")
                current_price = float(ticker_data.get("mark_price"))
                leverage = int(ticker_data.get("leverage"))
                lot_size = float(ticker_data.get("contract_value"))

                if delta_api.is_already_in_position_or_order(symbol):
                    print(f"Already in position for {symbol}")
                    continue

                # Uncomment to place order
                balance = delta_api.get_balance()
                balance_usd = balance.get("available_balance_usd")
                trade_setup = TradeCalculator.calculate_quantity(capital=float(balance_usd), mark_price=current_price, contract_value=lot_size, leverage=leverage, side=signal_type.lower())
                print("--------------[Trade Setup]------------------")
                print(f"Trade Setup: {trade_setup}")
                print("----------------------------------------------")
                delta_api.create_entry(
                    product_id=product_id,
                    size=trade_setup.get("quantity"),
                    side=signal_type.lower(),
                    entry_price=trade_setup.get("entry_price"),
                    leverage=leverage
                )

                print(f"Created entry for {symbol}")

        except Exception as e:
            print(f"Error in callback: {e}")


    delta_api = DeltaAPI(
        base_url='https://api.india.delta.exchange',
        api_key=config.api_key,
        api_secret=config.api_secret,
        client_id=config.client_id
    )
    # Create subscriber instance
    subscriber = RedisSubscriber()

    
    
    try:
        # Connect to Redis (automatically subscribes to channel)
        subscriber.connect()

        subscriber.add_callback_arguments(delta=delta_api)
        
        # Set callback function
        subscriber.set_callback(my_callback)
        
        # Start listening
        subscriber.start_listening()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        subscriber.stop_listening()


if __name__ == "__main__":
    main()





