"""
Position management service
"""

from typing import Dict, Any, List
from ..models import Account, PositionStatus
from ..core.response import TradeBuddyResponse
from .factory import RepositoryFactory


class PositionService:
    """Position management service"""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.position_repo = repository_factory.get_position_repository()
        self.order_repo = repository_factory.get_order_repository()
    
    async def get_positions(self, account: Account) -> Dict[str, Any]:
        """Get user positions with overview"""
        try:
            # Get today's positions (pending + today's completed)
            positions = await self.position_repo.get_todays_positions(account.account_id)
            
            # Get orders for each position
            for position in positions:
                orders = await self.order_repo.get_by_position(position.position_id)
                orders.sort(key=lambda x: x.order_datetime, reverse=True)
                position.orders = orders
            
            # Get all positions for total P&L calculation
            all_positions = await self.position_repo.get_by_account(account.account_id)
            
            # Calculate overview
            open_positions = [p for p in positions if p.position_status == PositionStatus.PENDING]
            closed_positions = [p for p in positions if p.position_status == PositionStatus.COMPLETED]
            
            total_pnl = sum(p.pnl_total for p in all_positions)
            todays_pnl = sum(p.pnl_total for p in positions)
            
            invested_amount = sum(
                abs(p.buy_margin - p.sell_margin) 
                for p in open_positions
            )
            
            overview = {
                "total_positions": len(positions),
                "open_positions": len(open_positions),
                "closed_positions": len(closed_positions),
                "pnl_todays": round(todays_pnl, 2),
                "positive_pnl_count": sum(1 for p in positions if p.pnl_total > 0),
                "negative_pnl_count": sum(1 for p in positions if p.pnl_total < 0),
                "balance": round(account.balance, 2),
                "invested_amount": round(invested_amount, 2),
                "pnl_total": round(total_pnl, 2)
            }
            
            return {
                "positions": [p.to_dict() for p in positions],
                "overview": overview
            }
            
        except Exception as e:
            raise Exception(f"Failed to retrieve positions: {str(e)}")
    
    async def get_all_positions(self, account: Account) -> List[Dict[str, Any]]:
        """Get all completed positions"""
        try:
            positions = await self.position_repo.get_completed_by_account(account.account_id)
            
            # Get orders for each position
            for position in positions:
                orders = await self.order_repo.get_by_position(position.position_id)
                orders.sort(key=lambda x: x.order_datetime, reverse=True)
                position.orders = orders
            
            return [p.to_dict() for p in positions]
            
        except Exception as e:
            raise Exception(f"Failed to retrieve position history: {str(e)}")