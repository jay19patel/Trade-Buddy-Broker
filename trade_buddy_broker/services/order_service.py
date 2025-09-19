"""
Order service for Trade Buddy SDK
"""

from typing import List, Optional
from datetime import datetime, timezone

from trade_buddy_broker.entities.models import Order, OrderType, OrderStatus, Position, PositionType
from trade_buddy_broker.repositories.order_repository import OrderRepository
from trade_buddy_broker.core.exceptions import TradeBuddyException, ValidationError


class OrderService:
    """Service for order management"""

    def __init__(self):
        self.order_repository = OrderRepository()

    async def create_position_orders(self, position: Position) -> List[Order]:
        """Create orders when a position is opened (buy + stoploss + target) - all PENDING initially"""
        orders = []

        try:
            # Create main buy/sell order - PENDING by default
            main_order = Order(
                position_id=position.position_id,
                account_id=position.account_id,
                symbol=position.symbol_id,
                order_type=OrderType.BUY if position.position_type == PositionType.LONG else OrderType.SELL,
                status=OrderStatus.PENDING,
                price=position.avg_price,
                quantity=position.quantity,
                notes=f"Position opening order - {position.position_type}"
            )
            orders.append(await self.order_repository.create(main_order))

            # Create stop loss order if stoploss is set
            if position.stoploss:
                stoploss_order = Order(
                    position_id=position.position_id,
                    account_id=position.account_id,
                    symbol=position.symbol_id,
                    order_type=OrderType.STOP_LOSS,
                    status=OrderStatus.PENDING,
                    price=position.stoploss,
                    quantity=position.remaining_quantity,
                    notes=f"Stop loss order for {position.position_type} position"
                )
                orders.append(await self.order_repository.create(stoploss_order))

            # Create target order if target is set
            if position.target:
                target_order = Order(
                    position_id=position.position_id,
                    account_id=position.account_id,
                    symbol=position.symbol_id,
                    order_type=OrderType.TARGET,
                    status=OrderStatus.PENDING,
                    price=position.target,
                    quantity=position.remaining_quantity,
                    notes=f"Target order for {position.position_type} position"
                )
                orders.append(await self.order_repository.create(target_order))

            return orders

        except Exception as e:
            raise TradeBuddyException(f"Failed to create position orders: {str(e)}")

    async def create_pyramid_order(self, position: Position, additional_quantity: float, new_price: float) -> Order:
        """Create order when pyramiding a position - PENDING by default"""
        try:
            pyramid_order = Order(
                position_id=position.position_id,
                account_id=position.account_id,
                symbol=position.symbol_id,
                order_type=OrderType.BUY if position.position_type == PositionType.LONG else OrderType.SELL,
                status=OrderStatus.PENDING,
                price=new_price,
                quantity=additional_quantity,
                notes=f"Pyramid order #{position.pyramid_count} - Adding to {position.position_type} position"
            )

            return await self.order_repository.create(pyramid_order)

        except Exception as e:
            raise TradeBuddyException(f"Failed to create pyramid order: {str(e)}")

    async def create_trailing_order(self, position: Position, close_quantity: float, exit_price: float) -> Order:
        """Create order when trailing (partial exit) a position - PENDING by default"""
        try:
            trailing_order = Order(
                position_id=position.position_id,
                account_id=position.account_id,
                symbol=position.symbol_id,
                order_type=OrderType.SELL if position.position_type == PositionType.LONG else OrderType.BUY,
                status=OrderStatus.PENDING,
                price=exit_price,
                quantity=close_quantity,
                notes=f"Trailing order #{position.trailing_count} - Partial exit from {position.position_type} position"
            )

            return await self.order_repository.create(trailing_order)

        except Exception as e:
            raise TradeBuddyException(f"Failed to create trailing order: {str(e)}")

    async def create_exit_order(self, position: Position, exit_price: float, close_quantity: Optional[float] = None) -> Order:
        """Create order when fully closing a position - PENDING by default"""
        try:
            quantity = close_quantity if close_quantity else position.remaining_quantity

            exit_order = Order(
                position_id=position.position_id,
                account_id=position.account_id,
                symbol=position.symbol_id,
                order_type=OrderType.SELL if position.position_type == PositionType.LONG else OrderType.BUY,
                status=OrderStatus.PENDING,
                price=exit_price,
                quantity=quantity,
                notes=f"Position exit order - Closing {position.position_type} position"
            )

            return await self.order_repository.create(exit_order)

        except Exception as e:
            raise TradeBuddyException(f"Failed to create exit order: {str(e)}")

    async def update_pending_orders_on_position_update(self, position: Position) -> List[Order]:
        """Update pending stop loss and target orders when position levels change"""
        try:
            # Get pending orders for this position
            orders = await self.order_repository.get_by_position_id(position.position_id)
            pending_orders = [order for order in orders if order.status == OrderStatus.PENDING]

            updated_orders = []

            for order in pending_orders:
                if order.order_type == OrderType.STOP_LOSS and position.stoploss:
                    order.price = position.stoploss
                    order.quantity = position.remaining_quantity
                    updated_orders.append(await self.order_repository.update(order))
                elif order.order_type == OrderType.TARGET and position.target:
                    order.price = position.target
                    order.quantity = position.remaining_quantity
                    updated_orders.append(await self.order_repository.update(order))

            return updated_orders

        except Exception as e:
            raise TradeBuddyException(f"Failed to update pending orders: {str(e)}")

    async def cancel_pending_orders(self, position_id: str) -> List[Order]:
        """Cancel all pending orders for a position when it's fully closed"""
        try:
            orders = await self.order_repository.get_by_position_id(position_id)
            pending_orders = [order for order in orders if order.status == OrderStatus.PENDING]

            cancelled_orders = []
            for order in pending_orders:
                order.status = OrderStatus.CANCELLED
                cancelled_orders.append(await self.order_repository.update(order))

            return cancelled_orders

        except Exception as e:
            raise TradeBuddyException(f"Failed to cancel pending orders: {str(e)}")

    async def get_orders_by_position(self, position_id: str) -> List[Order]:
        """Get all orders for a specific position"""
        return await self.order_repository.get_by_position_id(position_id)

    async def get_orders_by_account(self, account_id: str) -> List[Order]:
        """Get all orders for a specific account"""
        return await self.order_repository.get_by_account_id(account_id)

    async def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        return await self.order_repository.update_status(order_id, status)

    async def execute_order(self, order_id: str) -> Optional[Order]:
        """Execute a pending order by updating status and execution time"""
        try:
            order = await self.order_repository.get_by_id(order_id)
            if not order:
                raise TradeBuddyException(f"Order not found: {order_id}")

            if order.status != OrderStatus.PENDING:
                raise TradeBuddyException(f"Order {order_id} is not in PENDING status, current status: {order.status}")

            # Update order to executed
            order.status = OrderStatus.EXECUTED
            order.execution_time = datetime.now(timezone.utc)

            return await self.order_repository.update(order)

        except Exception as e:
            raise TradeBuddyException(f"Failed to execute order: {str(e)}")

    async def execute_orders_by_position(self, position_id: str, order_types: List[OrderType] = None) -> List[Order]:
        """Execute multiple orders for a position by type"""
        try:
            orders = await self.order_repository.get_by_position_id(position_id)
            pending_orders = [order for order in orders if order.status == OrderStatus.PENDING]

            if order_types:
                pending_orders = [order for order in pending_orders if order.order_type in order_types]

            executed_orders = []
            for order in pending_orders:
                executed_order = await self.execute_order(order.id)
                if executed_order:
                    executed_orders.append(executed_order)

            return executed_orders

        except Exception as e:
            raise TradeBuddyException(f"Failed to execute orders by position: {str(e)}")