"""
Position repository implementation
"""

from typing import List, Optional, Dict
from .base import BaseRepository
from trade_buddy.entities.models import Position, PositionStatus
from trade_buddy.core.exceptions import DataNotFoundError
from datetime import date


class PositionRepository(BaseRepository[Position]):
    """Repository for Position entities"""
    
    def __init__(self):
        self._positions: Dict[str, Position] = {}
        self._account_index: Dict[str, List[str]] = {}  # account_id -> [position_ids]
    
    async def create(self, position: Position) -> Position:
        """Create new position"""
        self._positions[position.position_id] = position
        
        # Update account index
        if position.account_id not in self._account_index:
            self._account_index[position.account_id] = []
        self._account_index[position.account_id].append(position.position_id)
        
        return position
    
    async def get_by_id(self, position_id: str) -> Optional[Position]:
        """Get position by ID"""
        return self._positions.get(position_id)
    
    async def get_by_account(self, account_id: str) -> List[Position]:
        """Get positions by account ID"""
        position_ids = self._account_index.get(account_id, [])
        return [self._positions[pos_id] for pos_id in position_ids if pos_id in self._positions]
    
    async def get_pending_by_account(self, account_id: str) -> List[Position]:
        """Get pending positions by account ID"""
        positions = await self.get_by_account(account_id)
        return [pos for pos in positions if pos.position_status == PositionStatus.PENDING]
    
    async def get_completed_by_account(self, account_id: str) -> List[Position]:
        """Get completed positions by account ID"""
        positions = await self.get_by_account(account_id)
        return [pos for pos in positions if pos.position_status == PositionStatus.COMPLETED]
    
    async def get_todays_positions(self, account_id: str) -> List[Position]:
        """Get today's positions by account ID"""
        positions = await self.get_by_account(account_id)
        today = date.today()
        
        filtered_positions = []
        for position in positions:
            position_date = position.created_date.date() if hasattr(position.created_date, 'date') else position.created_date
            if (position.position_status == PositionStatus.PENDING or 
                position_date == today):
                filtered_positions.append(position)
        
        return filtered_positions
    
    async def update(self, position: Position) -> Position:
        """Update position"""
        if position.position_id not in self._positions:
            raise DataNotFoundError("Position", position.position_id)
        
        self._positions[position.position_id] = position
        return position
    
    async def delete(self, position_id: str) -> bool:
        """Delete position"""
        if position_id not in self._positions:
            return False
        
        position = self._positions[position_id]
        del self._positions[position_id]
        
        # Update account index
        if position.account_id in self._account_index:
            if position_id in self._account_index[position.account_id]:
                self._account_index[position.account_id].remove(position_id)
        
        return True
    
    async def get_all(self) -> List[Position]:
        """Get all positions"""
        return list(self._positions.values())
    
    async def clear_all(self):
        """Clear all data (for testing)"""
        self._positions.clear()
        self._account_index.clear()