"""
Response models for Trade Buddy SDK
"""

from typing import Dict, Any, Optional
from trade_buddy.entities.response_schemas import TBResponse


class TradeBuddyResponse:
    """Legacy response class for backward compatibility"""
    
    def __init__(
        self, 
        message: str, 
        payload: Optional[Dict[str, Any]] = None, 
        success: bool = True
    ):
        self.message = message
        self.payload = payload or {}
        self.success = success
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "message": self.message,
            "payload": self.payload,
            "success": self.success
        }
        
    def __str__(self) -> str:
        return f"TradeBuddyResponse(success={self.success}, message='{self.message}')"
        
    def __repr__(self) -> str:
        return self.__str__()