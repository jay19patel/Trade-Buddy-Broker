"""
Response models for Trade Buddy SDK - Unified System
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class TBResponse(BaseModel):
    """
    Unified response format for all Trade Buddy broker methods
    """
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    
    class Config:
        from_attributes = True


# Alias for backward compatibility
TradeBuddyResponse = TBResponse