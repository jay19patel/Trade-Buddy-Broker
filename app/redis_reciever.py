
# ----------------------------- Redis Subscriber ----------------------------- #

from app.core.event import RedisSubscriber
from app.core.delta_api import DeltaAPI
from app.core.config import config
from typing import Callable, Optional, Dict, Any
import json
import signal
import sys
from app.core.trade_calculator import TradeCalculator
from app.core.logger import get_logger

# Initialize centralized logger
logger = get_logger('redis_receiver')

# Global subscriber instance for signal handling
subscriber_instance = None
shutdown_in_progress = False

def signal_handler(signum, frame):
    """Handle Ctrl+C and other termination signals"""
    global shutdown_in_progress
    
    if shutdown_in_progress:
        logger.info("Shutdown already in progress, forcing exit...")
        sys.exit(1)
    
    shutdown_in_progress = True
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    
    if subscriber_instance:
        logger.info("Stopping Redis subscription...")
        subscriber_instance.stop_listening()
        logger.info("Redis subscription stopped")
    
    logger.info("Graceful shutdown completed")
    sys.exit(0)

def main():
    """
    Example usage of RedisSubscriber class
    """
    def my_callback(channel: str, data: Dict[str, Any], **kwargs) -> None:
        try:
            # Log the complete received data for debugging
            logger.info(f"REDIS CALLBACK | Channel: {channel} | Data received: {json.dumps(data, indent=2)}")
            
            # data is already parsed JSON
            delta_api: DeltaAPI = kwargs.get("delta")
            results = data.get("data", {}).get("results", [])
            res_data = []

            if not results:
                logger.info("No results found in data. Skipping...")
                return

            for symbol_data in results:
                symbol = symbol_data.get("symbol")
                strategies = symbol_data.get("strategies", [])

                if not strategies:
                    logger.warning(f"No strategies for {symbol}")
                    continue

                # ✅ Pick the strategy with the highest confidence
                best_strategy = max(strategies, key=lambda s: s.get("confidence", 0.0))

                signal_type = best_strategy.get("signal_type")
                success = best_strategy.get("sucess", True)  # Keep typo as in source

                logger.info(f"STRATEGY ANALYSIS | Symbol: {symbol} | Best Strategy: {best_strategy.get('strategy_name')} | Confidence: {best_strategy.get('confidence')} | Signal: {signal_type}")

                # Skip HOLD or unsuccessful signals
                if signal_type == "HOLD" or not success:
                    logger.info(f"Skipping HOLD or failed strategy for {symbol}")
                    continue

                res_data.append(best_strategy)

            # ✅ Sort final selected strategies by confidence
            res_data = sorted(res_data, key=lambda x: x.get("confidence", 0), reverse=True)

            strategies_list = [f"{s.get('symbol')}:{s.get('strategy_name')}" for s in res_data]
            logger.info(f"FILTERED STRATEGIES | Count: {len(res_data)} | Strategies: {strategies_list}")

            # === Trading Execution ===
            for trade in res_data:
                symbol = trade.get("symbol")
                signal_type = trade.get("signal_type")
                
                logger.info(f"EXECUTING TRADE | Symbol: {symbol} | Signal: {signal_type}")

                ticker_data = delta_api.get_ticker(symbol)
                product_id = ticker_data.get("product_id")
                current_price = float(ticker_data.get("mark_price"))
                leverage = int(ticker_data.get("leverage"))
                lot_size = float(ticker_data.get("contract_value"))
                
                logger.info(f"TICKER DATA | Symbol: {symbol} | Price: {current_price} | Leverage: {leverage} | Lot Size: {lot_size}")

                if delta_api.is_already_in_position_or_order(symbol):
                    logger.info(f"Already in position for {symbol}")
                    continue

                # Uncomment to place order
                balance = delta_api.get_balance()
                balance_usd = balance.get("available_balance_usd")
                trade_setup = TradeCalculator.calculate_quantity(capital=float(balance_usd), mark_price=current_price, contract_value=lot_size, leverage=leverage, side=signal_type.lower())
                
                logger.info(f"TRADE SETUP | Balance: ${balance_usd} | Quantity: {trade_setup.get('quantity')} | Entry Price: {trade_setup.get('entry_price')}")
                
                delta_api.create_entry(
                    product_id=product_id,
                    size=trade_setup.get("quantity"),
                    side=signal_type.lower(),
                    entry_price=trade_setup.get("entry_price"),
                    leverage=leverage
                )

                logger.info(f"ENTRY ORDER CREATED | Symbol: {symbol} | Side: {signal_type.lower()} | Size: {trade_setup.get('quantity')}")

        except Exception as e:
            logger.error(f"Error in callback: {e}", exc_info=True)


    delta_api = DeltaAPI(
        base_url='https://api.india.delta.exchange',
        api_key=config.api_key,
        api_secret=config.api_secret,
        client_id=config.client_id
    )
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    # Create subscriber instance
    global subscriber_instance
    subscriber = RedisSubscriber()
    subscriber_instance = subscriber  # Store globally for signal handler
    
    try:
        # Check if shutdown is already in progress
        if shutdown_in_progress:
            logger.info("Shutdown in progress, not starting Redis subscriber")
            return
            
        logger.info("Starting Redis subscriber...")
        
        # Connect to Redis (automatically subscribes to channel)
        subscriber.connect()

        subscriber.add_callback_arguments(delta=delta_api)
        
        # Set callback function
        subscriber.set_callback(my_callback)
        
        # Start listening
        logger.info("Starting to listen for Redis messages...")
        subscriber.start_listening()
        
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        logger.info("Stopping Redis subscriber...")
        subscriber.stop_listening()
        logger.info("Redis subscriber stopped")


if __name__ == "__main__":
    main()





