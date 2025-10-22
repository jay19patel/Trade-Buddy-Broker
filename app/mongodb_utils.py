#!/usr/bin/env python3
"""
MongoDB utility functions for order and position management
Simple, clean functions for data storage and retrieval
"""

from pymongo import MongoClient
from app.config import config
from datetime import datetime
from app.logger import get_logger

# Use centralized logger
logger = get_logger('database')


class DatabaseManager:
    """Simple database manager for orders and positions"""
    
    def __init__(self):
        self.mongo_client = MongoClient(config.mongodb_url)
        self.db = self.mongo_client[config.mongodb_database]
        self.orders_collection = self.db['orders']
        self.positions_collection = self.db['positions']
    
    @staticmethod
    def create_order(order_data):
        """
        Store order data as received (no modification)
        
        Args:
            order_data: Complete order data dictionary
            
        Returns:
            str: Order ID if successful, None if failed
        """
        try:
            # Add timestamp
            order_data['created_at'] = datetime.now()
            
            # Get database connection
            mongo_client = MongoClient(config.mongodb_url)
            db = mongo_client[config.mongodb_database]
            orders_collection = db['orders']
            
            # Insert order
            result = orders_collection.insert_one(order_data)
            order_id = str(result.inserted_id)
            
            logger.info(f"Order created successfully: {order_id}")
            mongo_client.close()
            
            return order_id
            
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            return None
    
    @staticmethod
    def create_position(position_data):
        """
        Store position data as received (no modification)
        
        Args:
            position_data: Complete position data dictionary
            
        Returns:
            str: Position ID if successful, None if failed
        """
        try:
            # Add timestamp
            position_data['created_at'] = datetime.now()
            position_data['status'] = 'open'
            
            # Get database connection
            mongo_client = MongoClient(config.mongodb_url)
            db = mongo_client[config.mongodb_database]
            positions_collection = db['positions']
            
            # Insert position
            result = positions_collection.insert_one(position_data)
            position_id = str(result.inserted_id)
            
            logger.info(f"Position created successfully: {position_id}")
            mongo_client.close()
            
            return position_id
            
        except Exception as e:
            logger.error(f"Failed to create position: {e}")
            return None
    
    @staticmethod
    def close_position(position):
        """
        Find and close open position for given symbol
        
        Args:
            symbol: Symbol to close position for
            
        Returns:
            bool: True if position closed successfully, False otherwise
        """
        try:
            # Get database connection
            mongo_client = MongoClient(config.mongodb_url)
            db = mongo_client[config.mongodb_database]
            positions_collection = db['positions']
            
            # Find open position
            update_position = positions_collection.find_one({
                'product_symbol': position.get('product_symbol'),
                'product_id': position.get('product_id'),
                'status': 'open'
            })
            if not position:
                logger.warning(f"No open position found for symbol: {position.get('product_symbol')}")
                mongo_client.close()
                return False
            
            # Update position to closed

            update_data = {
                'status': 'closed',
                'close_at': datetime.now(),
                'realized_pnl': position.get('realized_pnl'),
                'realized_funding': position.get('realized_funding'),
                'realized_cashflow': position.get('realized_cashflow'),
                'commission': position.get('commission'),
                'liquidation_price': position.get('liquidation_price'),
            }
            
            result = positions_collection.update_one(
                {'_id': update_position['_id']},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Position closed successfully for symbol: {position.get('product_symbol')}")
                mongo_client.close()
                return True
            else:
                logger.error(f"Failed to close position for symbol: {position.get('product_symbol')}")
                mongo_client.close()
                return False
                
        except Exception as e:
            logger.error(f"Error closing position for {position.get('product_symbol')}: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        self.mongo_client.close()
        logger.info("Database connection closed")

