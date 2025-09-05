"""
Async DB-backed Position repository (SQLModel/SQLAlchemy AsyncSession)
"""

from typing import List, Optional
from sqlalchemy import select, update
from trade_buddy.entities.models import Position, PositionStatus
from trade_buddy.core.database import get_database_manager


class PositionRepository:
    async def create(self, position: Position) -> Position:
        db = get_database_manager()
        async for session in db.get_session():
            try:
                session.add(position)
                await session.commit()
                return position
            except Exception as e:
                await session.rollback()
                raise e

    async def get_by_id(self, position_id: str) -> Optional[Position]:
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Position).where(Position.position_id == position_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_open_by_account(self, account_id: str) -> List[Position]:
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Position).where(
                Position.account_id == account_id,
                Position.status == PositionStatus.OPEN.value
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_history_by_account(self, account_id: str) -> List[Position]:
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Position).where(
                Position.account_id == account_id,
                Position.status == PositionStatus.CLOSED.value
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_levels(self, position_id: str, stoploss: float | None, target: float | None) -> bool:
        db = get_database_manager()
        async for session in db.get_session():
            values = {}
            if stoploss is not None:
                values["stoploss"] = stoploss
            if target is not None:
                values["target"] = target
            if not values:
                return True
            stmt = (
                update(Position)
                .where(Position.position_id == position_id)
                .values(**values)
            )
            await session.execute(stmt)
            await session.commit()
            return True

    async def close(self, position_id: str, exit_price: float, pnl: float, pnl_percentage: float):
        db = get_database_manager()
        async for session in db.get_session():
            from datetime import datetime
            stmt = (
                update(Position)
                .where(Position.position_id == position_id)
                .values(
                    status=PositionStatus.CLOSED.value,
                    exit_price=exit_price,
                    pnl=pnl,
                    pnl_percentage=pnl_percentage,
                    realized_pnl=pnl,
                    unrealized_pnl=0.0,
                    closed_at=datetime.now(),
                )
            )
            await session.execute(stmt)
            await session.commit()
            return True


