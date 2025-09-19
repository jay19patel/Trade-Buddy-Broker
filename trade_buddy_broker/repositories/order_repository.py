"""
Order repository for Trade Buddy SDK
"""

from typing import List, Optional
from sqlmodel import select

from trade_buddy_broker.entities.models import Order, OrderStatus, OrderType
from trade_buddy_broker.repositories.base import BaseRepository
from trade_buddy_broker.core.database import get_database_manager
from trade_buddy_broker.core.exceptions import TradeBuddyException


class OrderRepository(BaseRepository[Order]):
    """Repository for order operations"""

    def __init__(self):
        self.db_manager = get_database_manager()

    async def create(self, order: Order) -> Order:
        """Create new order"""
        try:
            async for session in self.db_manager.get_session():
                session.add(order)
                await session.commit()
                await session.refresh(order)
                return order
        except Exception as e:
            raise TradeBuddyException(f"Failed to create order: {str(e)}")

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            async for session in self.db_manager.get_session():
                statement = select(Order).where(Order.id == order_id)
                result = await session.execute(statement)
                return result.scalar_one_or_none()
        except Exception as e:
            raise TradeBuddyException(f"Failed to get order: {str(e)}")

    async def update(self, order: Order) -> Order:
        """Update order"""
        try:
            async for session in self.db_manager.get_session():
                # Use merge to handle object from different session
                merged_order = await session.merge(order)
                await session.commit()
                await session.refresh(merged_order)
                return merged_order
        except Exception as e:
            raise TradeBuddyException(f"Failed to update order: {str(e)}")

    async def delete(self, order_id: str) -> bool:
        """Delete order"""
        try:
            async for session in self.db_manager.get_session():
                statement = select(Order).where(Order.id == order_id)
                result = await session.execute(statement)
                order = result.scalar_one_or_none()
                if order:
                    await session.delete(order)
                    await session.commit()
                    return True
                return False
        except Exception as e:
            raise TradeBuddyException(f"Failed to delete order: {str(e)}")

    async def get_all(self) -> List[Order]:
        """Get all orders"""
        try:
            async for session in self.db_manager.get_session():
                statement = select(Order)
                result = await session.execute(statement)
                return result.scalars().all()
        except Exception as e:
            raise TradeBuddyException(f"Failed to get all orders: {str(e)}")

    async def get_by_position_id(self, position_id: str) -> List[Order]:
        """Get all orders for a specific position"""
        try:
            async for session in self.db_manager.get_session():
                statement = select(Order).where(Order.position_id == position_id)
                result = await session.execute(statement)
                return result.scalars().all()
        except Exception as e:
            raise TradeBuddyException(f"Failed to get orders by position: {str(e)}")

    async def get_by_account_id(self, account_id: str) -> List[Order]:
        """Get all orders for a specific account"""
        try:
            async for session in self.db_manager.get_session():
                statement = select(Order).where(Order.account_id == account_id)
                result = await session.execute(statement)
                return result.scalars().all()
        except Exception as e:
            raise TradeBuddyException(f"Failed to get orders by account: {str(e)}")

    async def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders by status"""
        try:
            async for session in self.db_manager.get_session():
                statement = select(Order).where(Order.status == status)
                result = await session.execute(statement)
                return result.scalars().all()
        except Exception as e:
            raise TradeBuddyException(f"Failed to get orders by status: {str(e)}")

    async def get_by_type(self, order_type: OrderType) -> List[Order]:
        """Get orders by type"""
        try:
            async for session in self.db_manager.get_session():
                statement = select(Order).where(Order.order_type == order_type)
                result = await session.execute(statement)
                return result.scalars().all()
        except Exception as e:
            raise TradeBuddyException(f"Failed to get orders by type: {str(e)}")

    async def update_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        try:
            order = await self.get_by_id(order_id)
            if order:
                order.status = status
                if status == OrderStatus.EXECUTED:
                    from datetime import datetime, timezone
                    order.execution_time = datetime.now(timezone.utc)
                return await self.update(order)
            return None
        except Exception as e:
            raise TradeBuddyException(f"Failed to update order status: {str(e)}")