"""
Custom exceptions for Trade Buddy SDK
"""

from typing import Optional


class TradeBuddyException(Exception):
    """Base exception for Trade Buddy SDK"""
    
    def __init__(
        self, 
        message: str, 
        resolution: Optional[str] = None, 
        status_code: int = 400
    ):
        self.message = message
        self.resolution = resolution or "Please try again"
        self.status_code = status_code
        super().__init__(self.message)
        
    def to_dict(self) -> dict:
        """Convert exception to dictionary"""
        return {
            "message": self.message,
            "resolution": self.resolution,
            "status_code": self.status_code
        }


class AuthenticationError(TradeBuddyException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            resolution="Please login again",
            status_code=401
        )


class ValidationError(TradeBuddyException):
    """Validation related errors"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            resolution="Please check your input data",
            status_code=400
        )


class InsufficientFundsError(TradeBuddyException):
    """Insufficient funds error"""
    
    def __init__(self, available_balance: float = None):
        message = "Insufficient funds for this operation"
        if available_balance is not None:
            message += f". Available balance: ₹{available_balance:,.2f}"
        
        super().__init__(
            message=message,
            resolution="Please add funds to your account",
            status_code=400
        )


class PositionNotFoundError(TradeBuddyException):
    """Position not found error"""
    
    def __init__(self, position_id: str):
        super().__init__(
            message=f"Position {position_id} not found or already closed",
            resolution="Please check the position ID",
            status_code=404
        )


class OrderCreationError(TradeBuddyException):
    """Order creation error"""
    
    def __init__(self, message: str):
        super().__init__(
            message=f"Order creation failed: {message}",
            resolution="Please verify order details and try again",
            status_code=400
        )


class DataNotFoundError(TradeBuddyException):
    """Data not found error"""
    
    def __init__(self, resource: str, identifier: str = ""):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
            
        super().__init__(
            message=message,
            resolution=f"Please check the {resource.lower()} details",
            status_code=404
        )