"""
Main broker class - Production ready Trade Buddy SDK
"""

import asyncio
from typing import Optional, List, Dict, Any

from trade_buddy.entities.models import Account
from trade_buddy.entities.schemas import (
    RegistrationSchema, LoginSchema, CreateOrderSchema,
    UpdateStoplossSchema, UpdateQuantitySchema, ExitOrderSchema,
    TransactionSchema, SupportTicketSchema
)
from trade_buddy.core.exceptions import AuthenticationError, ValidationError, TradeBuddyException
from trade_buddy.core.response import TradeBuddyResponse
from trade_buddy.services.factory import ServiceFactory


class TradeBuddy:
    """
    Main Trade Buddy Broker SDK Class - Production Ready
    
    A comprehensive paper trading platform with enterprise-grade architecture:
    - Repository Pattern for data access
    - Factory Pattern for service creation  
    - Singleton Pattern for shared resources
    - Comprehensive error handling
    - Clean separation of concerns
    
    Usage:
        broker = TradeBuddy()
        
        # Register user
        response = await broker.registration(registration_data)
        
        # Login
        response = await broker.login(login_data)
        
        # Create order
        response = await broker.create_order(order_data)
        
        # Get positions  
        positions = await broker.get_positions()
    """
    
    def __init__(self):
        """Initialize Trade Buddy broker"""
        self._service_factory = ServiceFactory()
        self._current_account: Optional[Account] = None
        self._access_token: Optional[str] = None
        self._initialized = False
    
    async def _initialize_demo_data(self):
        """Initialize with demo account"""
        if self._initialized:
            return
        
        try:
            auth_service = self._service_factory.create_service('auth')
            
            # Create demo account
            from trade_buddy.utils.security import SecurityManager
            security = SecurityManager()
            
            demo_account = Account(
                account_id="DEMO01",
                full_name="Demo User",
                email_id="demo@tradebuddy.com",
                password=security.generate_hash_password("demo123"),
                balance=100000.0,
                email_verified=True,
                description="Demo account for testing"
            )
            
            repo_factory = self._service_factory.get_repository_factory()
            account_repo = repo_factory.get_account_repository()
            
            try:
                await account_repo.create(demo_account)
            except TradeBuddyException:
                pass  # Account already exists
            
            self._initialized = True
            
        except Exception:
            pass  # Silent fail for demo data
    
    def _require_authentication(self):
        """Check if user is authenticated"""
        if not self._current_account or not self._access_token:
            raise AuthenticationError("Please login first")
    
    async def registration(self, data: Dict[str, Any]) -> TradeBuddyResponse:
        """
        Register new user
        
        Args:
            data: Registration data dictionary
            
        Returns:
            TradeBuddyResponse with account details
        """
        try:
            # Validate input
            if isinstance(data, dict):
                schema = RegistrationSchema(**data)
            else:
                schema = data
            
            auth_service = self._service_factory.create_service('auth')
            return await auth_service.register(schema)
            
        except ValidationError:
            raise
        except Exception as e:
            raise TradeBuddyException(f"Registration failed: {str(e)}")
    
    async def login(self, data: Dict[str, Any]) -> TradeBuddyResponse:
        """
        Login user
        
        Args:
            data: Login data dictionary
            
        Returns:
            TradeBuddyResponse with login details and access token
        """
        try:
            # Initialize demo data if not done
            if not self._initialized:
                await self._initialize_demo_data()
            
            # Validate input
            if isinstance(data, dict):
                schema = LoginSchema(**data)
            else:
                schema = data
            
            auth_service = self._service_factory.create_service('auth')
            response = await auth_service.login(schema)
            
            # Store session
            self._access_token = response.payload.get('access_token')
            account = await auth_service.verify_token(self._access_token)
            self._current_account = account
            
            return response
            
        except (ValidationError, AuthenticationError):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Login failed: {str(e)}")
    
    async def create_order(self, data: Dict[str, Any]) -> TradeBuddyResponse:
        """
        Create new order
        
        Args:
            data: Order data dictionary
            
        Returns:
            TradeBuddyResponse with order details
        """
        self._require_authentication()
        
        try:
            # Validate input
            if isinstance(data, dict):
                schema = CreateOrderSchema(**data)
            else:
                schema = data
            
            order_service = self._service_factory.create_service('order')
            return await order_service.create_new_order(self._current_account, schema)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Order creation failed: {str(e)}")
    
    async def update_stoploss(self, data: Dict[str, Any]) -> TradeBuddyResponse:
        """Create/update stoploss order"""
        self._require_authentication()
        
        try:
            if isinstance(data, dict):
                schema = UpdateStoplossSchema(**data)
            else:
                schema = data
            
            order_service = self._service_factory.create_service('order')
            return await order_service.create_stoploss_order(self._current_account, schema)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Stoploss update failed: {str(e)}")
    
    async def update_quantity(self, data: Dict[str, Any]) -> TradeBuddyResponse:
        """Update position quantity"""
        self._require_authentication()
        
        try:
            if isinstance(data, dict):
                schema = UpdateQuantitySchema(**data)
            else:
                schema = data
            
            order_service = self._service_factory.create_service('order')
            return await order_service.update_quantity(self._current_account, schema)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Quantity update failed: {str(e)}")
    
    async def exit_position(self, data: Dict[str, Any]) -> TradeBuddyResponse:
        """Exit position completely"""
        self._require_authentication()
        
        try:
            if isinstance(data, dict):
                schema = ExitOrderSchema(**data)
            else:
                schema = data
            
            order_service = self._service_factory.create_service('order')
            return await order_service.exit_position(self._current_account, schema)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Position exit failed: {str(e)}")
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get user positions with overview"""
        self._require_authentication()
        
        try:
            position_service = self._service_factory.create_service('position')
            return await position_service.get_positions(self._current_account)
            
        except Exception as e:
            raise TradeBuddyException(f"Failed to retrieve positions: {str(e)}")
    
    async def get_position_history(self) -> List[Dict[str, Any]]:
        """Get all completed positions"""
        self._require_authentication()
        
        try:
            position_service = self._service_factory.create_service('position')
            return await position_service.get_all_positions(self._current_account)
            
        except Exception as e:
            raise TradeBuddyException(f"Failed to retrieve position history: {str(e)}")
    
    async def create_transaction(self, data: Dict[str, Any]) -> TradeBuddyResponse:
        """Create transaction (deposit/withdraw)"""
        self._require_authentication()
        
        try:
            if isinstance(data, dict):
                schema = TransactionSchema(**data)
            else:
                schema = data
            
            transaction_service = self._service_factory.create_service('transaction')
            return await transaction_service.create_transaction(self._current_account, schema)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Transaction failed: {str(e)}")
    
    async def get_account_details(self) -> Dict[str, Any]:
        """Get current account details"""
        self._require_authentication()
        return self._current_account.to_dict()
    
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for stock/option symbols"""
        try:
            price_service = self._service_factory.create_service('price')
            return price_service.search_symbols(query)
        except Exception as e:
            raise TradeBuddyException(f"Symbol search failed: {str(e)}")
    
    def get_live_price(self, symbol_id: str, symbol_type: str = "Stocks") -> Optional[Dict[str, Any]]:
        """Get live price for a symbol"""
        try:
            price_service = self._service_factory.create_service('price')
            return price_service.get_stock_price(symbol_id, symbol_type)
        except Exception as e:
            raise TradeBuddyException(f"Price fetch failed: {str(e)}")
    
    def get_multiple_prices(self, symbols: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Get live prices for multiple symbols"""
        try:
            price_service = self._service_factory.create_service('price')
            return price_service.get_multiple_prices(symbols)
        except Exception as e:
            raise TradeBuddyException(f"Multiple price fetch failed: {str(e)}")
    
    async def send_support_ticket(self, data: Dict[str, Any]) -> TradeBuddyResponse:
        """Send support ticket"""
        try:
            if isinstance(data, dict):
                schema = SupportTicketSchema(**data)
            else:
                schema = data
            
            from trade_buddy.entities.models import Ticket
            from trade_buddy.utils.security import SecurityManager
            
            security = SecurityManager()
            ticket = Ticket(
                id=security.generate_unique_id("TKT"),
                email=schema.email,
                title=schema.title,
                message=schema.message
            )
            
            return TradeBuddyResponse(
                message=f"Support ticket created successfully",
                payload={"ticket_id": ticket.id}
            )
            
        except ValidationError:
            raise
        except Exception as e:
            raise TradeBuddyException(f"Failed to create support ticket: {str(e)}")
    
    async def verify_email(self, token: str) -> TradeBuddyResponse:
        """Verify email with token"""
        try:
            auth_service = self._service_factory.create_service('auth')
            return await auth_service.verify_email(token)
            
        except (ValidationError, AuthenticationError):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Email verification failed: {str(e)}")
    
    async def logout(self):
        """Logout current user"""
        self._current_account = None
        self._access_token = None
    
    # Additional utility methods
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self._current_account is not None and self._access_token is not None
    
    def get_current_balance(self) -> float:
        """Get current account balance"""
        self._require_authentication()
        return self._current_account.balance
    
    async def clear_all_data(self):
        """Clear all data (for testing purposes only)"""
        repo_factory = self._service_factory.get_repository_factory()
        repo_factory.clear_all_repositories()
        self._current_account = None
        self._access_token = None