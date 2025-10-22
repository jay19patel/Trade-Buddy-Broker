from app.delta_websoket import DeltaWebSocketClient
from app.config import config
from app.delta_api import DeltaAPI
from app.mongodb_utils import DatabaseManager
from app.logger import get_logger
from app.trade_calculator import TradeCalculator
# Initialize centralized logger
logger = get_logger('delta_listener')

# Initialize Delta API
delta_api = DeltaAPI(
    base_url='https://api.india.delta.exchange',
    api_key=config.api_key,
    api_secret=config.api_secret,
    client_id=config.client_id
)

def orders_handle(orders: list) -> None:
    """
    Handle order updates from Delta WebSocket and store in database
    """
    if not orders:
        logger.info("No orders found in update")
        return

    logger.info(f"Processing {len(orders)} order(s)")
    
    for order in orders:
        try:
            action = order.get('action', 'unknown')
            order_id = order.get('id')
            symbol = order.get('product_symbol', order.get('symbol', 'unknown'))
            
            logger.info(f"Processing order: ID={order_id}, Symbol={symbol}, Action={action}")
            
            # Store order directly as received (no modification)
            stored_order_id = DatabaseManager.create_order(order)
            if stored_order_id:
                logger.info(f"Order stored in MongoDB with ID: {stored_order_id}")
            else:
                logger.error(f"Failed to store order: {order_id}")
            
        except Exception as e:
            logger.error(f"Error processing order {order.get('id', 'unknown')}: {str(e)}", exc_info=True)

def ticker_handle(ticker_data: dict) -> None:
    """
    Handle ticker updates from Delta WebSocket and log ticker data
    """
    try:
        symbol = ticker_data.get('symbol', 'unknown')
        last_price = ticker_data.get('close', ticker_data.get('last_price', 0))
        volume = ticker_data.get('volume', 0)
        change_24h = ticker_data.get('change_24h', 0)
        high_24h = ticker_data.get('high_24h', 0)
        low_24h = ticker_data.get('low_24h', 0)
        
        # Log ticker data with detailed information
        logger.info(f"📊 TICKER UPDATE | Symbol: {symbol} | Price: {last_price} | Volume: {volume} | "
                   f"24h Change: {change_24h}% | High: {high_24h} | Low: {low_24h}")
        
    except Exception as e:
        logger.error(f"Error processing ticker data: {str(e)}", exc_info=True)

def positions_handle(positions: list) -> None:
    """
    Handle position updates from Delta WebSocket
    """
    if not positions:
        logger.info("No Positions found.")
        return

    for position in positions:
        try:
            action = position.get('action', None)
            symbol = position.get('symbol')
            
            if action and action.lower() == "create":
                logger.info(f"New Position Created: {symbol}")
                # Store position directly as received (no modification)
                
                side = "buy" if position.get('size', 0) > 0 else "sell"
        
                # Calculate stop loss and target
                stop_target = TradeCalculator.calculate_stop_target(
                    current_price=float(position.get('entry_price', 0)),
                    side=side,
                    liquidation_price=float(position.get('liquidation_price', 0))
                )

                delta_api.create_stoploss_target(
                    product_id=position.get('product_id'),
                    symbol=position.get('product_symbol'),
                    stoploss_price=stop_target.get('stop_loss'),
                    target_price=stop_target.get('target')
                )
                logger.info(f"Stop loss and target orders created for {position.get('symbol')}")

                stored_position_id = DatabaseManager.create_position(position)
                if stored_position_id:
                    logger.info(f"Position stored in MongoDB with ID: {stored_position_id}")
                else:
                    logger.error(f"Failed to store position: {symbol}")
                
            elif action and action.lower() == "delete":
                logger.info(f"Position Deleted: {symbol}")
                # Close position using symbol
                if DatabaseManager.close_position(position):
                    logger.info(f"Position closed successfully: {symbol}")
                else:
                    logger.error(f"Failed to close position: {symbol}")
                    
        except Exception as e:
            logger.error(f"Error processing position {position.get('symbol', 'unknown')}: {str(e)}", exc_info=True)

# WebSocket subscriptions
subscriptions = {
    "orders": ["all"],
    "positions": ["all"],
    "ticker": ["all"]
}

# Initialize WebSocket client
client = DeltaWebSocketClient(
    websocket_url=config.websocket_url,
    api_key=config.api_key,
    api_secret=config.api_secret,
    subscriptions=subscriptions,
    orders_callback=orders_handle,
    positions_callback=positions_handle,
    ticker_callback=ticker_handle,
)

if __name__ == "__main__":
    try:
        logger.info("Starting Delta WebSocket listener...")
        client.connect()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down...")
        client.disconnect()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        client.disconnect()
    finally:
        logger.info("Delta WebSocket listener stopped")






