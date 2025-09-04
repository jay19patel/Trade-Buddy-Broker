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
        quantity: int,
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
            stoploss=stoploss,
            target=target,
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


