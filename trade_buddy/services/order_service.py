"""
Order management service
"""

from typing import Dict, Any
from ..models import (
    Account, Position, Order, OrderSide, PositionStatus, 
    OrderTypes, ProductType, CreateBy
)
from ..schemas import (
    CreateOrderSchema, UpdateStoplossSchema,
    UpdateQuantitySchema, ExitOrderSchema
)
from ..core.exceptions import (
    InsufficientFundsError, PositionNotFoundError, 
    OrderCreationError, ValidationError
)
from ..core.response import TradeBuddyResponse
from ..utils.security import SecurityManager
from .factory import RepositoryFactory


class OrderService:
    """Order management service"""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.position_repo = repository_factory.get_position_repository()
        self.order_repo = repository_factory.get_order_repository()
        self.account_repo = repository_factory.get_account_repository()
        self.security = SecurityManager()
    
    async def create_new_order(self, account: Account, data: CreateOrderSchema) -> TradeBuddyResponse:
        """Create new order"""
        try:
            order_margin = data.quantity * data.price
            
            # Check balance
            if order_margin > account.balance:
                raise InsufficientFundsError(account.balance)
            
            position_id = self.security.generate_unique_id("POS")
            
            # Create position
            position = Position(
                position_id=position_id,
                account_id=account.account_id,
                stock_symbol=data.stock_symbol,
                stock_type=data.stock_type,
                created_by=data.created_by,
                stoploss_price=data.stoploss_price,
                target_price=data.target_price,
                position_side=data.order_side
            )
            
            if data.order_side == OrderSide.BUY:
                position.buy_average = data.price
                position.buy_quantity = data.quantity
                position.buy_margin = order_margin
            else:
                position.sell_average = data.price
                position.sell_quantity = data.quantity
                position.sell_margin = order_margin
            
            # Create order
            order = Order(
                order_id=self.security.generate_unique_id("ORD"),
                account_id=account.account_id,
                position_id=position_id,
                stock_symbol=data.stock_symbol,
                order_types=OrderTypes.NewOrder,
                order_side=data.order_side,
                product_type=ProductType.CNC,
                stop_order_activate=True,
                price=data.price,
                stoploss_price=data.stoploss_price,
                target_price=data.target_price,
                quantity=data.quantity,
                created_by=data.created_by
            )
            
            # Update account balance
            account.balance -= order_margin
            
            # Save entities
            await self.position_repo.create(position)
            await self.order_repo.create(order)
            await self.account_repo.update(account)
            
            return TradeBuddyResponse(
                message=f"New position created for {data.stock_symbol}",
                payload={
                    "position_id": position.position_id,
                    "order_id": order.order_id,
                    "account_balance": account.balance
                }
            )
            
        except Exception as e:
            if isinstance(e, (InsufficientFundsError, ValidationError)):
                raise
            raise OrderCreationError(str(e))
    
    async def create_stoploss_order(self, account: Account, data: UpdateStoplossSchema) -> TradeBuddyResponse:
        """Create stoploss order"""
        try:
            position = await self.position_repo.get_by_id(data.position_id)
            
            if not position or position.position_status != PositionStatus.PENDING:
                raise PositionNotFoundError(data.position_id)
            
            # Update position prices
            if data.target_price is not None:
                position.target_price = data.target_price
            if data.stoploss_price is not None:
                position.stoploss_price = data.stoploss_price
            
            # Deactivate previous stoploss orders
            existing_orders = await self.order_repo.get_by_position(position.position_id)
            for order in existing_orders:
                if order.order_types in [OrderTypes.StopLossOrder, OrderTypes.NewOrder] and order.stop_order_activate:
                    order.stop_order_activate = False
                    await self.order_repo.update(order)
            
            # Create new stoploss order
            order = Order(
                order_id=self.security.generate_unique_id("ORD"),
                account_id=account.account_id,
                position_id=position.position_id,
                stock_symbol=position.stock_symbol,
                order_types=OrderTypes.StopLossOrder,
                product_type=position.product_type,
                stoploss_price=data.stoploss_price,
                target_price=data.target_price,
                quantity=data.quantity,
                created_by=data.created_by,
                stop_order_activate=True
            )
            
            await self.position_repo.update(position)
            await self.order_repo.create(order)
            
            return TradeBuddyResponse(
                message="Stop-loss order created/updated",
                payload={
                    "position_id": position.position_id,
                    "order_id": order.order_id
                }
            )
            
        except Exception as e:
            if isinstance(e, (PositionNotFoundError, ValidationError)):
                raise
            raise OrderCreationError(str(e))
    
    async def update_quantity(self, account: Account, data: UpdateQuantitySchema) -> TradeBuddyResponse:
        """Update position quantity"""
        try:
            position = await self.position_repo.get_by_id(data.position_id)
            
            if not position or position.position_status != PositionStatus.PENDING:
                raise PositionNotFoundError(data.position_id)
            
            current_qty = abs(position.buy_quantity - position.sell_quantity)
            
            # Validate quantity for opposite side orders
            if (data.order_side != position.position_side) and (data.quantity > current_qty):
                raise ValidationError("Quantity exceeds available position")
            
            order_margin = data.quantity * data.price
            
            # Check balance for same side orders
            if order_margin > account.balance and position.position_side == data.order_side:
                raise InsufficientFundsError(account.balance)
            
            # Update position based on order side
            if data.order_side == OrderSide.BUY:
                new_qty = position.buy_quantity + data.quantity
                position.buy_average = round((
                    (position.buy_average * position.buy_quantity + data.price * data.quantity) / new_qty
                ), 2)
                position.buy_quantity = new_qty
                position.buy_margin += order_margin
            else:
                new_qty = position.sell_quantity + data.quantity
                position.sell_average = round((
                    (position.sell_average * position.sell_quantity + data.price * data.quantity) / new_qty
                ), 2)
                position.sell_quantity = new_qty
                position.sell_margin += order_margin
            
            # Update account balance
            balance_change = -order_margin if position.position_side == data.order_side else order_margin
            account.balance += balance_change
            
            # Check if position is fully closed
            order_type = OrderTypes.UpdateQtyOrder
            message = f"Quantity updated for {data.order_side.value}"
            
            if position.buy_quantity == position.sell_quantity:
                pnl = (position.sell_average - position.buy_average) * position.sell_quantity
                position.pnl_total += pnl
                position.position_status = PositionStatus.COMPLETED
                message = f"Position closed with P&L: ₹{pnl:,.2f}"
                order_type = OrderTypes.ExitOrder
            
            # Create order
            order = Order(
                order_id=self.security.generate_unique_id("ORD"),
                account_id=account.account_id,
                position_id=position.position_id,
                stock_symbol=position.stock_symbol,
                order_types=order_type,
                order_side=data.order_side,
                product_type=ProductType.CNC,
                price=data.price,
                quantity=data.quantity,
                created_by=data.created_by
            )
            
            await self.position_repo.update(position)
            await self.order_repo.create(order)
            await self.account_repo.update(account)
            
            return TradeBuddyResponse(
                message=message,
                payload={
                    "position_id": position.position_id,
                    "order_id": order.order_id,
                    "account_balance": account.balance
                }
            )
            
        except Exception as e:
            if isinstance(e, (PositionNotFoundError, InsufficientFundsError, ValidationError)):
                raise
            raise OrderCreationError(str(e))
    
    async def exit_position(self, account: Account, data: ExitOrderSchema) -> TradeBuddyResponse:
        """Exit position completely"""
        try:
            position = await self.position_repo.get_by_id(data.position_id)
            
            if not position or position.position_status != PositionStatus.PENDING:
                raise PositionNotFoundError(data.position_id)
            
            exit_qty = abs(position.buy_quantity - position.sell_quantity)
            exit_side = OrderSide.SELL if position.position_side == OrderSide.BUY else OrderSide.BUY
            order_margin = exit_qty * data.price
            
            # Update position
            if position.position_side == OrderSide.BUY:
                new_sell_qty = position.sell_quantity + exit_qty
                position.sell_average = (
                    (position.sell_average * position.sell_quantity + data.price * exit_qty) / new_sell_qty
                ) if new_sell_qty > 0 else data.price
                position.sell_quantity = new_sell_qty
                position.sell_margin += order_margin
            else:
                new_buy_qty = position.buy_quantity + exit_qty
                position.buy_average = (
                    (position.buy_average * position.buy_quantity + data.price * exit_qty) / new_buy_qty
                ) if new_buy_qty > 0 else data.price
                position.buy_quantity = new_buy_qty
                position.buy_margin += order_margin
            
            # Calculate P&L and close position
            pnl = (position.sell_average - position.buy_average) * position.sell_quantity
            position.pnl_total += pnl
            position.position_status = PositionStatus.COMPLETED
            
            # Update account balance
            account.balance += order_margin
            
            # Create exit order
            order = Order(
                order_id=self.security.generate_unique_id("ORD"),
                account_id=account.account_id,
                position_id=position.position_id,
                stock_symbol=position.stock_symbol,
                order_types=OrderTypes.ExitOrder,
                order_side=exit_side,
                product_type=position.product_type,
                stop_order_hit=True,
                price=data.price,
                quantity=exit_qty,
                created_by=data.created_by
            )
            
            await self.position_repo.update(position)
            await self.order_repo.create(order)
            await self.account_repo.update(account)
            
            return TradeBuddyResponse(
                message=f"Position exited with P&L: ₹{pnl:,.2f}",
                payload={
                    "position_id": position.position_id,
                    "order_id": order.order_id,
                    "pnl": pnl,
                    "account_balance": account.balance
                }
            )
            
        except Exception as e:
            if isinstance(e, (PositionNotFoundError, ValidationError)):
                raise
            raise OrderCreationError(str(e))