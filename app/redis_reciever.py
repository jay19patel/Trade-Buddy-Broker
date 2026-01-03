
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

            delta_api: DeltaAPI = kwargs.get("delta")

            balance = delta_api.get_balance()
            balance_usd = balance.get("available_balance_usd")
            logger.info(f"BALANCE | Balance: ${balance_usd}")
                
            # Log the complete received data for debugging
            logger.info(f"REDIS CALLBACK | Channel: {channel} | Data received: {json.dumps(data, indent=2)}")
            
            # data is already parsed JSON
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
                success = best_strategy.get("success", True)  # Keep typo as in source

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
                symbol = trade.get("symbol").replace("-", "")
                signal_type = trade.get("signal_type")
                
                logger.info(f"EXECUTING TRADE | Symbol: {symbol} | Signal: {signal_type}")

                ticker_data = delta_api.get_ticker(symbol)
                product_id = ticker_data.get("product_id")
                current_price = float(ticker_data.get("mark_price"))
                leverage = int(ticker_data.get("leverage"))
                lot_size = float(ticker_data.get("contract_value"))
                
                logger.info(f"TICKER DATA | Symbol: {symbol} | Price: {current_price} | Leverage: {leverage} | Lot Size: {lot_size}")

                # Logic branching: If Exit on Signal is enabled, handle Flip/Hold logic.
                # If disabled, use strict "Skip used symbol" logic.
                should_skip = False
                
                if config.exit_on_signal:
                    active_pos = delta_api.get_active_position(symbol)
                    if active_pos:
                        pos_size = float(active_pos.get('size', 0))
                        current_side = 'buy' if pos_size > 0 else 'sell'
                        
                        if current_side != signal_type.lower():
                            logger.info(f"FLIP SIGNAL: Existing {current_side} position vs New {signal_type} signal. Closing...")
                            delta_api.close_position(product_id, symbol)
                            import time
                            time.sleep(2) # Wait for closure to process
                            should_skip = True # Skip creating new order, as per user request (Only close)
                        else:
                            logger.info(f"Signal matches existing {current_side} position. Holding/Skipping.")
                            should_skip = True
                    else:
                        # No active position.
                        # Do we check for open orders? Standard behavior usually implies yes.
                        # But user request "don't use already logic" implies if exit_on_signal is true, we rely on position check.
                        # However, to be safe against double ordering on lag, we should check orders if no position.
                        # But strictly following user: "if exit on signal, don't use the already check".
                        # So if we are here (no pos), we proceed.
                        pass
                else:
                    # Strict check: If ANY position or order exists, skip.
                    if delta_api.is_already_in_position_or_order(symbol):
                         logger.info(f"Already in position/order for {symbol}. Skipping.")
                         should_skip = True

                if should_skip:
                    continue

                trade_setup = TradeCalculator.calculate_quantity(capital=float(balance_usd), mark_price=current_price, contract_value=lot_size, leverage=leverage, side=signal_type.lower())
                
                # Use the calculated safe leverage
                execution_leverage = trade_setup.get("leverage")
                safe_limit = trade_setup.get("safe_leverage_limit")

                logger.info(f"TRADE SETUP | Balance: ${balance_usd} | Quantity: {trade_setup.get('quantity')} | Entry Price: {trade_setup.get('entry_price')} | Provided Lev: {leverage} | Safe Lev Limit: {safe_limit} | Executing Lev: {execution_leverage} | Used Capital: ${trade_setup.get('used_capital')}")
                
                delta_api.create_entry(
                    product_id=product_id,
                    size=trade_setup.get("quantity"),
                    side=signal_type.lower(),
                    entry_price=trade_setup.get("entry_price"),
                    leverage=execution_leverage
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





