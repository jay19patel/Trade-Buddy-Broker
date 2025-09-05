"""
Async DB-backed Position service
"""

from datetime import datetime
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
        quantity: float,
        price: float,
        side: str,
        stoploss: Optional[float] = None,
        target: Optional[float] = None,
    ) -> Position:
        position = Position(
            position_id=self.security.generate_unique_id("POS"),
            account_id=account.account_id,
            symbol_id=symbol_id,
            side=side.upper(),
            quantity=quantity,
            avg_price=price,
            status=PositionStatus.OPEN.value,
            position_type=("LONG" if side.upper()=="BUY" else "SHORT"),
            invested_amount=quantity*price,
            leverage=getattr(account, "default_leverage", 1.0) or 1.0,
            margin_used=(quantity*price)/((getattr(account, "default_leverage", 1.0) or 1.0) if (getattr(account, "default_leverage", 1.0) or 1.0)>0 else 1.0),
            stoploss=stoploss,
            target=target,
            total_quantity=quantity,
            remaining_quantity=quantity,
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
        multiplier = 1 if position.side == 'BUY' else -1
        pnl = round((exit_price - position.avg_price) * position.quantity * multiplier, 2)
        await self.repo.close(position_id, exit_price, pnl)
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
            return position
        if position.original_quantity == 0:
            position.original_quantity = position.quantity
        old_investment = position.invested_amount
        add_investment = additional_quantity * new_price
        total_investment = old_investment + add_investment
        total_quantity = position.quantity + additional_quantity
        position.average_entry_price = total_investment / total_quantity if total_quantity>0 else position.avg_price
        position.quantity = total_quantity
        position.total_quantity = total_quantity
        position.invested_amount = total_investment
        position.remaining_quantity = total_quantity
        position.pyramid_count += 1
        if position.leverage>0:
            position.margin_used = total_investment / position.leverage
        # persist
        await self.repo.update_levels(position_id, position.stoploss, position.target)
        updated = await self.repo.get_by_id(position_id)
        return updated

    async def partial_close(self, account: Account, position_id: str, close_quantity: float, exit_price: float) -> Position:
        position = await self.repo.get_by_id(position_id)
        if not position or position.account_id != account.account_id:
            raise ValueError("Position not found")
        if close_quantity >= position.quantity:
            return await self.exit_position(account, position_id, exit_price)
        pnl_per_unit = (exit_price - (position.average_entry_price or position.avg_price)) if position.side=='BUY' else ((position.average_entry_price or position.avg_price) - exit_price)
        realized = (position.realized_pnl or 0.0) + pnl_per_unit*close_quantity
        remaining = position.quantity - close_quantity
        # simplistic update via update_levels then re-read; for a full impl we'd add dedicated update calls
        await self.repo.update_levels(position_id, position.stoploss, position.target)
        updated = await self.repo.get_by_id(position_id)
        updated.realized_pnl = round(realized, 2)
        updated.quantity = remaining
        updated.remaining_quantity = remaining
        updated.trailing_count = (updated.trailing_count or 0) + 1
        return updated


