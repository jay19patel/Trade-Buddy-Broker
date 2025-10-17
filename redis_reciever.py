
# ----------------------------- Redis Subscriber ----------------------------- #


from app.event import RedisSubscriber
from app.delta_api import DeltaAPI
from app.config import config
from typing import Callable, Optional, Dict, Any
import json


def main():
    """
    Example usage of RedisSubscriber class
    """
    def my_callback(channel: str, data: Dict[str, Any],**kwargs) -> None:
        try:
       # data is already parsed JSON, no need to parse again
            delta_api : DeltaAPI = kwargs.get("delta")
            res_data = []
            result = data.get("data", {}).get("results", [])
            if result and len(result) > 0:
                for symbol_data in result:
                    symbol = symbol_data.get("symbol")
                    strategies = symbol_data.get("strategies", [])  
                    print(f"Symbol: {symbol} Strategies: {strategies}")
                    for strategy in strategies:
                        signal_type = strategy.get("signal_type")
                        success = strategy.get("sucess", False)  # Note: keeping the typo as it appears in the data
                        if signal_type != "HOLD" and success:
                            res_data.append(strategy)
                        else:
                            print(f"SKIPPING HOLD SIGNAL for {symbol} - {strategy.get('strategy_name')}")
            res_data = sorted(res_data, key=lambda x: x.get("confidence"), reverse=True)
            print(f"Res data: {res_data}")
            # [{'strategy_name': 'EMA Crossover Strategy', 'symbol': 'ETH-USD', 'signal_type': 'BUY', 'confidence': 0.9, 'execution_time': 0.2605619430541992, 'timestamp': '2025-10-16T17:26:26.215781+00:00', 'price': 3500.25, 'created_at': '2025-10-16 17:27:27.052658+00:00', '_id': '68f12affa35bc12cbe3ca58c', 'sucess': True}, {'strategy_name': 'Bollinger Bands Mean Reversion Strategy', 'symbol': 'BTC-USD', 'signal_type': 'BUY', 'confidence': 0.85, 'execution_time': 0.2602965831756592, 'timestamp': '2025-10-16T17:26:26.215781+00:00', 'price': 67500.5, 'created_at': '2025-10-16 17:27:27.047146+00:00', '_id': '68f12aff8b680056ab3ca58a', 'sucess': True}, {'strategy_name': 'MACD Convergence Divergence Strategy', 'symbol': 'BTC-USD', 'signal_type': 'SELL', 'confidence': 0.75, 'execution_time': 0.36953139305114746, 'timestamp': '2025-10-16T17:26:26.215781+00:00', 'price': 67500.5, 'created_at': '2025-10-16 17:27:27.157807+00:00', '_id': '68f12affcc5b501c1c3ca58b', 'sucess': True}]
            for trade in res_data:
                symbol = trade.get("symbol")
                signal_type = trade.get("signal_type")

                ticker_data = delta_api.get_ticker(symbol)
                product_id = ticker_data.get('product_id')
                current_price = float(ticker_data.get('mark_price'))
                leverage = ticker_data.get('leverage')
                if delta_api.is_already_in_position_or_order(symbol):
                    print(f"Already in position for {symbol}")
                    continue
                else:
                    delta_api.create_entry(
                        product_id=product_id,
                        size=1,
                        side=signal_type.lower(),
                        entry_price=current_price * 1.01, # 1% above current price
                        leverage=leverage
                    )
                    print(f"Created entry for {symbol}")
            # return res_data
        except Exception as e:
            print(f"Error: {e}")

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





