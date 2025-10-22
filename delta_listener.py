from app.delta_websoket import DeltaWebSocketClient
from app.config import config
import time
from app.delta_api import DeltaAPI
from app.trade_calculator import TradeCalculator
from datetime import datetime
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Delta API
delta_api = DeltaAPI(
    base_url='https://api.india.delta.exchange',
    api_key=config.api_key,
    api_secret=config.api_secret,
    client_id=config.client_id
)

# Initialize MongoDB connection
mongo_client = MongoClient(config.mongodb_url)
db = mongo_client[config.mongodb_database]
positions_collection = db[config.mongodb_positions_collection]

def positions_handle(positions: list) -> None:
    """
    Handle position updates from Delta WebSocket
    """
    if not positions:
        logger.info("No Positions found.")
        return

    for position in positions:
        action = position.get('action', None)
        symbol = position.get('symbol')
        
        if action and action.lower() == "create":
            logger.info(f"New Position Created: {symbol}")
            handle_position_create(position)
            
        elif action and action.lower() == "delete":
            logger.info(f"Position Deleted: {symbol}")
            handle_position_delete(position)

def handle_position_create(position: dict) -> None:
    """
    Handle position creation - store in MongoDB and create stop/target orders
    """
    try:
        # Calculate side based on size
        side = "buy" if position.get('size', 0) > 0 else "sell"
        
        # Calculate stop loss and target
        stop_target = TradeCalculator.calculate_stop_target(
            current_price=float(position.get('entry_price', 0)),
            side=side,
            liquidation_price=float(position.get('liquidation_price', 0))
        )
        
        # Prepare position document for MongoDB
        position_doc = {
            'symbol': position.get('symbol'),
            'product_symbol': position.get('product_symbol'),
            'product_id': position.get('product_id'),
            'user_id': position.get('user_id'),
            'side': side,
            'size': position.get('size'),
            'entry_price': float(position.get('entry_price', 0)),
            'liquidation_price': float(position.get('liquidation_price', 0)),
            'bankruptcy_price': float(position.get('bankruptcy_price', 0)),
            'margin': float(position.get('margin', 0)),
            'margin_mode': position.get('margin_mode'),
            'commission': float(position.get('commission', 0)),
            'realized_cashflow': float(position.get('realized_cashflow', 0)),
            'realized_funding': float(position.get('realized_funding', 0)),
            'realized_pnl': float(position.get('realized_pnl', 0)),
            'adl_level': position.get('adl_level'),
            'auto_topup': position.get('auto_topup', False),
            'under_liquidation': position.get('under_liquidation', False),
            'reason': position.get('reason'),
            'status': 'open',
            'entry_datetime': datetime.fromtimestamp(position.get('timestamp', 0) / 1000000),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            # Stop loss and target prices
            'stop_loss_price': stop_target.get('stop_loss'),
            'target_price': stop_target.get('target'),
            'liquidation_warning_price': stop_target.get('liquidation_warning_price'),
            # Execution tracking
            'holding_time_minutes': 0,
            'close_datetime': None,
            'close_price': None,
            'total_commission': float(position.get('commission', 0)),
            'total_pnl': 0.0
        }
        
        # Insert position into MongoDB
        result = positions_collection.insert_one(position_doc)
        logger.info(f"Position stored in MongoDB with ID: {result.inserted_id}")
        
        # Create stop loss and target orders
        delta_api.create_stoploss_target(
            product_id=position.get('product_id'),
            symbol=position.get('product_symbol'),
            stoploss_price=stop_target.get('stop_loss'),
            target_price=stop_target.get('target')
        )
        logger.info(f"Stop loss and target orders created for {position.get('symbol')}")
        
    except Exception as e:
        logger.error(f"Error handling position create for {position.get('symbol')}: {str(e)}")

def handle_position_delete(position: dict) -> None:
    """
    Handle position deletion - update MongoDB with close data
    """
    try:
        symbol = position.get('symbol')
        product_id = position.get('product_id')
        
        # Find the open position in MongoDB
        open_position = positions_collection.find_one({
            'symbol': symbol,
            'product_id': product_id,
            'status': 'open'
        })
        
        if not open_position:
            logger.warning(f"No open position found for {symbol} to close")
            return
        
        # Calculate holding time
        entry_datetime = open_position['entry_datetime']
        close_datetime = datetime.now()
        holding_time_minutes = (close_datetime - entry_datetime).total_seconds() / 60
        
        # Calculate final PnL and commission
        current_commission = float(position.get('commission', 0))
        current_pnl = float(position.get('realized_pnl', 0))
        total_commission = open_position.get('total_commission', 0) + current_commission
        total_pnl = current_pnl  # This should be the final realized PnL
        
        # Update position in MongoDB
        update_data = {
            'status': 'closed',
            'close_datetime': close_datetime,
            'close_price': float(position.get('entry_price', 0)),  # Current price when closed
            'holding_time_minutes': round(holding_time_minutes, 2),
            'total_commission': total_commission,
            'total_pnl': total_pnl,
            'updated_at': close_datetime,
            'final_realized_pnl': current_pnl,
            'final_commission': current_commission
        }
        
        result = positions_collection.update_one(
            {'_id': open_position['_id']},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            logger.info(f"Position {symbol} closed successfully. "
                       f"Holding time: {holding_time_minutes:.2f} minutes, "
                       f"Total PnL: {total_pnl}, "
                       f"Total Commission: {total_commission}")
        else:
            logger.error(f"Failed to update position {symbol} in MongoDB")
            
    except Exception as e:
        logger.error(f"Error handling position delete for {symbol}: {str(e)}")

# WebSocket subscriptions
subscriptions = {
    "orders": ["all"],
    "positions": ["all"]
}

# Initialize WebSocket client
client = DeltaWebSocketClient(
    websocket_url=config.websocket_url,
    api_key=config.api_key,
    api_secret=config.api_secret,
    subscriptions=subscriptions,
    orders_callback=None,
    positions_callback=positions_handle,
    ticker_callback=None,
)

if __name__ == "__main__":
    try:
        logger.info("Starting Delta WebSocket listener...")
        client.connect()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        mongo_client.close()