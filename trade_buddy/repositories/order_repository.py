"""
Order repository implementation
"""

from typing import List, Optional, Dict
from .base import BaseRepository
from trade_buddy.entities.models import Order
from trade_buddy.core.exceptions import DataNotFoundError


class OrderRepository(BaseRepository[Order]):
    """Repository for Order entities"""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
        self._account_index: Dict[str, List[str]] = {}  # account_id -> [order_ids]
        self._position_index: Dict[str, List[str]] = {}  # position_id -> [order_ids]
    
    async def create(self, order: Order) -> Order:
        """Create new order"""
        self._orders[order.order_id] = order
        
        # Update account index
        if order.account_id not in self._account_index:
            self._account_index[order.account_id] = []
        self._account_index[order.account_id].append(order.order_id)
        
        # Update position index
        if order.position_id not in self._position_index:
            self._position_index[order.position_id] = []
        self._position_index[order.position_id].append(order.order_id)
        
        return order
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self._orders.get(order_id)
    
    async def get_by_account(self, account_id: str) -> List[Order]:
        """Get orders by account ID"""
        order_ids = self._account_index.get(account_id, [])
        return [self._orders[order_id] for order_id in order_ids if order_id in self._orders]
    
    async def get_by_position(self, position_id: str) -> List[Order]:
        """Get orders by position ID"""
        order_ids = self._position_index.get(position_id, [])
        return [self._orders[order_id] for order_id in order_ids if order_id in self._orders]
    
    async def update(self, order: Order) -> Order:
        """Update order"""
        if order.order_id not in self._orders:
            raise DataNotFoundError("Order", order.order_id)
        
        self._orders[order.order_id] = order
        return order
    
    async def delete(self, order_id: str) -> bool:
        """Delete order"""
        if order_id not in self._orders:
            return False
        
        order = self._orders[order_id]
        del self._orders[order_id]
        
        # Update indexes
        if order.account_id in self._account_index:
            if order_id in self._account_index[order.account_id]:
                self._account_index[order.account_id].remove(order_id)
        
        if order.position_id in self._position_index:
            if order_id in self._position_index[order.position_id]:
                self._position_index[order.position_id].remove(order_id)
        
        return True
    
    async def get_all(self) -> List[Order]:
        """Get all orders"""
        return list(self._orders.values())
    
    async def clear_all(self):
        """Clear all data (for testing)"""
        self._orders.clear()
        self._account_index.clear()
        self._position_index.clear()