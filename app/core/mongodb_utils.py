#!/usr/bin/env python3
"""
MongoDB utility functions for order and position management
Simple, clean functions for data storage and retrieval
"""

from pymongo import MongoClient
from .config import config
from datetime import datetime
from .logger import get_logger

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
    def update_position(position_data):
        """
        Update open position with new data
        
        Args:
            position_data: Dictionary containing position updates
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            mongo_client = MongoClient(config.mongodb_url)
            db = mongo_client[config.mongodb_database]
            positions_collection = db['positions']
            
            # Find open position to update
            # We match by product_id and product_symbol and status='open'
            # The 'action' field in position_data is 'update', but we don't store that.
            
            filter_query = {
                'product_symbol': position_data.get('product_symbol') or position_data.get('symbol'),
                'product_id': position_data.get('product_id'),
                'status': 'open'
            }
            
            # We want to update fields present in position_data.
            # Excluding fields that shouldn't change identity (like _id) or logic if passed.
            # But simpler to just $set whatever comes in, except maybe 'action'.
            
            update_fields = {k: v for k, v in position_data.items() if k not in ['_id', 'action', 'type']}
            update_fields['updated_at'] = datetime.now()
            
            result = positions_collection.update_one(
                filter_query,
                {'$set': update_fields}
            )
            
            mongo_client.close()
            
            if result.modified_count > 0:
                logger.info(f"Position updated successfully: {position_data.get('symbol')}")
                return True
            else:
                # It might be that no fields changed, or no position found
                logger.debug(f"No position updated for {position_data.get('symbol')} (maybe no changes or not found)")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update position: {e}")
            return False

    @staticmethod
    def update_order(order_data):
        """
        Update existing order with new data
        
        Args:
            order_data: Dictionary containing order updates
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            mongo_client = MongoClient(config.mongodb_url)
            db = mongo_client[config.mongodb_database]
            orders_collection = db['orders']
            
            # Find order by 'id' (exchange order id)
            order_id = order_data.get('id')
            if not order_id:
                logger.warning("No order ID provided for update")
                mongo_client.close()
                return False
                
            filter_query = {'id': order_id}
            
            update_fields = {k: v for k, v in order_data.items() if k not in ['_id', 'action', 'type']}
            update_fields['updated_at'] = datetime.now()
            
            result = orders_collection.update_one(
                filter_query,
                {'$set': update_fields}
            )
            
            mongo_client.close()
            
            if result.modified_count > 0:
                logger.info(f"Order updated successfully: {order_id}")
                return True
            else:
                logger.debug(f"No order updated for {order_id} (maybe no changes or not found)")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update order: {e}")
            return False

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

