"""
Async DB-backed Position service
"""

from typing import List, Optional

from trade_buddy.entities.models import Account, Position, PositionStatus
from trade_buddy.repositories.position_repository import PositionRepository
from trade_buddy.utils.security import SecurityManager


class PositionService:
    def __init__(self):
        self.repo = PositionRepository()
        self.security = SecurityManager()

    async def open_position(
        self,
        account: Account,
        symbol_id: str,
        remaining_quantity: float,
        price: float,
        side: str,
        stoploss: Optional[float] = None,
        target: Optional[float] = None,
    ) -> Position:
        leverage = getattr(account, "default_leverage", 1.0) or 1.0
        if leverage <= 0:
            leverage = 1.0
        
        invested_amount = remaining_quantity * price
        margin_required = invested_amount / leverage
        
        # Check available margin
        available_margin = getattr(account, "available_margin", account.balance)
        if available_margin < margin_required:
            raise ValueError(f"Insufficient funds. Required margin: ₹{margin_required:.2f}, Available: ₹{available_margin:.2f}")
        
        # Update account margins first
        try:
            from trade_buddy.repositories.account_repository import AccountRepository
            acc_repo = AccountRepository()
            
            # Update margin calculations
            account.utilized_margin = (getattr(account, "utilized_margin", 0.0) or 0.0) + margin_required
            account.total_margin = max(getattr(account, "total_margin", 0.0) or 0.0, account.utilized_margin)
            account.available_margin = max(account.balance - account.utilized_margin, 0.0)
            account.margin_percentage = (account.utilized_margin / account.balance * 100) if account.balance > 0 else 0.0
            
            await acc_repo.update(account)
        except Exception as e:
            raise ValueError(f"Failed to update account margins: {str(e)}")
        
        position = Position(
            position_id=self.security.generate_unique_id("POS"),
            account_id=account.account_id,
            symbol_id=symbol_id,
            side=side.upper(),
            remaining_quantity=remaining_quantity,
            avg_price=price,
            status=PositionStatus.OPEN.value,
            position_type=("LONG" if side.upper()=="BUY" else "SHORT"),
            invested_amount=invested_amount,
            leverage=leverage,
            margin_used=margin_required,
            stoploss=stoploss,
            target=target,
            quantity=remaining_quantity,
            average_entry_price=price,
        )
        return await self.repo.create(position)

    async def update_levels(
        self,
        account: Account,
        position_id: str,
        stoploss: Optional[float] = None,
        target: Optional[float] = None,
    ) -> Position:
        position = await self.repo.get_by_id(position_id)
        if not position or position.account_id != account.account_id:
            raise ValueError("Position not found")
        await self.repo.update_levels(position_id, stoploss, target)
        updated = await self.repo.get_by_id(position_id)
        return updated

    async def exit_position(self, account: Account, position_id: str, exit_price: float) -> Position:
        position = await self.repo.get_by_id(position_id)
        if not position or position.account_id != account.account_id:
            raise ValueError("Position not found")
        if position.status != PositionStatus.OPEN.value:
            raise ValueError("Position is already closed")
        
        # Calculate PnL
        entry_price = position.average_entry_price or position.avg_price
        multiplier = 1 if position.side == 'BUY' else -1
        remaining_pnl = round((exit_price - entry_price) * position.remaining_quantity * multiplier, 2)
        # Add any existing realized PnL from partial exits
        total_pnl = remaining_pnl + (position.realized_pnl or 0.0)
        pnl = round(total_pnl, 2)
        pnl_pct = round((pnl / position.invested_amount) * 100, 4) if position.invested_amount else 0.0
        
        # Release all margin from this position
        position_margin = position.margin_used or 0.0
        
        # Update account balance with PnL and release margin
        try:
            from trade_buddy.repositories.account_repository import AccountRepository
            acc_repo = AccountRepository()
            # Add PnL to balance and release margin
            account.balance = (getattr(account, "balance", 0.0) or 0.0) + pnl
            account.utilized_margin = max((getattr(account, "utilized_margin", 0.0) or 0.0) - position_margin, 0.0)
            account.available_margin = max(account.balance - account.utilized_margin, 0.0)
            account.margin_percentage = (account.utilized_margin / account.balance * 100) if account.balance > 0 else 0.0
            await acc_repo.update(account)
        except Exception:
            pass
        
        await self.repo.close(position_id, exit_price, pnl, pnl_pct)
        closed = await self.repo.get_by_id(position_id)
        return closed

    async def get_open_positions(self, account_id: str) -> List[Position]:
        return await self.repo.get_open_by_account(account_id)

    async def get_position_history(self, account_id: str) -> List[Position]:
        return await self.repo.get_history_by_account(account_id)

    async def add_to_position(self, account: Account, position_id: str, additional_quantity: float, new_price: float) -> Position:
        position = await self.repo.get_by_id(position_id)
        if not position or position.account_id != account.account_id:
            raise ValueError("Position not found")
        if position.status != PositionStatus.OPEN.value:
            raise ValueError("Cannot add to closed position")
        
        # Calculate additional investment and margin required
        position_leverage = position.leverage if position.leverage and position.leverage > 0 else 1.0
        add_investment = additional_quantity * new_price
        additional_margin = add_investment / position_leverage
        
        # Check available margin
        available_margin = getattr(account, "available_margin", 0.0)
        if available_margin < additional_margin:
            raise ValueError(f"Insufficient funds for pyramiding. Required margin: ₹{additional_margin:.2f}, Available: ₹{available_margin:.2f}")
        
        # Compute new totals
        current_quantity = position.remaining_quantity
        old_investment = position.invested_amount or (position.avg_price * current_quantity)
        total_investment = old_investment + add_investment
        new_total_quantity = current_quantity + additional_quantity
        new_average_entry = total_investment / new_total_quantity if new_total_quantity > 0 else position.avg_price
        
        # Update quantity to track total remaining_quantity ever held
        new_original_quantity = position.quantity + additional_quantity

        # Update account margin usage
        try:
            from trade_buddy.repositories.account_repository import AccountRepository
            acc_repo = AccountRepository()
            account.utilized_margin = (getattr(account, "utilized_margin", 0.0) or 0.0) + additional_margin
            account.total_margin = max(getattr(account, "total_margin", 0.0) or 0.0, account.utilized_margin)
            account.available_margin = max(account.balance - account.utilized_margin, 0.0)
            account.margin_percentage = (account.utilized_margin / account.balance * 100) if account.balance > 0 else 0.0
            await acc_repo.update(account)
        except Exception as e:
            raise ValueError(f"Failed to update account margins: {str(e)}")

        # Persist position changes
        new_position_margin_used = (getattr(position, "margin_used", 0.0) or 0.0) + additional_margin

        position_values = {
            "remaining_quantity": new_total_quantity,
            "quantity": new_original_quantity,
            "invested_amount": total_investment,
            "pyramid_count": (position.pyramid_count or 0) + 1,
            "average_entry_price": new_average_entry,
            "avg_price": new_average_entry,
            "margin_used": new_position_margin_used,
        }
        await self.repo.update_pyramiding(position_id, position_values)
        updated = await self.repo.get_by_id(position_id)
        return updated

    async def partial_close(self, account: Account, position_id: str, close_quantity: float, exit_price: float) -> Position:
        position = await self.repo.get_by_id(position_id)
        if not position or position.account_id != account.account_id:
            raise ValueError("Position not found")
        
        # Validation: Check if trying to close more remaining_quantity than available
        if close_quantity > position.remaining_quantity:
            raise ValueError(f"Cannot close {close_quantity} remaining_quantity. Only {position.remaining_quantity} remaining_quantity is available in position.")
        
        # Calculate realized PnL for the closing leg
        entry_avg = position.average_entry_price or position.avg_price
        pnl_per_unit = (exit_price - entry_avg) if position.side == 'BUY' else (entry_avg - exit_price)
        close_realized = pnl_per_unit * close_quantity
        realized_total = round((position.realized_pnl or 0.0) + close_realized, 2)

        # Update average exit price weighted by exited remaining_quantity
        # Calculate how much was previously exited: quantity - current_quantity
        prev_exit_qty = (position.quantity - position.remaining_quantity) if (position.quantity and position.remaining_quantity is not None) else 0.0
        if prev_exit_qty < 0:
            prev_exit_qty = 0.0
        total_exit_qty = prev_exit_qty + close_quantity
        if total_exit_qty > 0:
            weighted_exit_sum = (position.average_exit_price or 0.0) * prev_exit_qty + (exit_price * close_quantity)
            new_avg_exit = weighted_exit_sum / total_exit_qty
        else:
            new_avg_exit = position.average_exit_price or 0.0

        # Margin release proportional to remaining_quantity closed
        position_margin_used = (position.margin_used or 0.0)
        released_margin = position_margin_used * (close_quantity / position.remaining_quantity)

        remaining = position.remaining_quantity - close_quantity

        # Persist position updates atomically
        await self.repo.update_partial(position_id, {
            "remaining_quantity": remaining,
            "realized_pnl": realized_total,
            "average_exit_price": new_avg_exit,
            "trailing_count": (position.trailing_count or 0) + 1,
            "margin_used": max(position_margin_used - released_margin, 0.0),
        })

        # Update account margins accordingly
        try:
            from trade_buddy.repositories.account_repository import AccountRepository
            acc_repo = AccountRepository()
            account.utilized_margin = max((getattr(account, "utilized_margin", 0.0) or 0.0) - released_margin, 0.0)
            account.available_margin = max(account.balance - account.utilized_margin, 0.0)
            account.margin_percentage = (account.utilized_margin / account.balance * 100) if account.balance > 0 else 0.0
            await acc_repo.update(account)
        except Exception:
            pass

        updated = await self.repo.get_by_id(position_id)
        # If remaining becomes zero due to rounding, close the position fully at average exit
        if updated.remaining_quantity <= 0:
            return await self.exit_position(account, position_id, exit_price)
        return updated


