"""
Main broker class - Production ready Trade Buddy SDK with Database Integration
"""

import asyncio
from typing import Optional, List, Dict, Any

from trade_buddy.entities.models import Account
from trade_buddy.entities.schemas import (
    RegistrationSchema, LoginSchema, CreateOrderSchema,
    UpdateStoplossSchema, UpdateQuantitySchema, ExitOrderSchema,
    TransactionSchema, SupportTicketSchema
)
from trade_buddy.entities.response_schemas import (
    UserData, LoginData, OrderData, PositionData,
    TransactionData, TicketData, PositionsOverview, AccountData,
    SymbolData, PriceData
)
from trade_buddy.core.exceptions import AuthenticationError, ValidationError, TradeBuddyException
from trade_buddy.core.response import TBResponse
from trade_buddy.core.database import get_database_manager, initialize_database
from trade_buddy.core.session_manager import HybridSessionManager, SessionData
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
        self._session_manager = HybridSessionManager()
        self._current_session_id: Optional[str] = None
        self._initialized = False
        self._db_initialized = False
    
    async def _initialize_database(self):
        """Initialize database tables"""
        if not self._db_initialized:
            await initialize_database()
            self._db_initialized = True
    
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
    
    async def _require_authentication(self) -> SessionData:
        """Check if user is authenticated and return session"""
        if not self._current_session_id:
            raise AuthenticationError("Please login first")
        
        session = await self._session_manager.get_session(self._current_session_id)
        if not session:
            raise AuthenticationError("Session expired, please login again")
        
        # Validate session token
        if not await self._session_manager.validate_session(self._current_session_id):
            raise AuthenticationError("Invalid session, please login again")
        
        return session
    
    async def registration(self, data: Dict[str, Any]) -> TBResponse:
        """
        Register new user
        
        Args:
            data: Registration data dictionary
            
        Returns:
            TBResponse with user account details
        """
        try:
            # Initialize database if not done
            await self._initialize_database()
            
            # Validate input
            if isinstance(data, dict):
                schema = RegistrationSchema(**data)
            else:
                schema = data
            
            auth_service = self._service_factory.create_service('auth')
            response = await auth_service.register(schema)
            
            # Convert to new TBResponse format
            if response.success:
                user_data = UserData(**response.payload['user'])
                return TBResponse(
                    message="Registration successful",
                    data={"user": user_data.model_dump()}
                )
            else:
                return TBResponse(message=response.message, data=None)
            
        except ValidationError:
            raise
        except Exception as e:
            raise TradeBuddyException(f"Registration failed: {str(e)}")
    
    async def login(self, data: Dict[str, Any]) -> TBResponse:
        """
        Login user
        
        Args:
            data: Login data dictionary
            
        Returns:
            TBResponse with login details and access token
        """
        try:
            # Initialize database and demo data if not done
            await self._initialize_database()
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
            if response.success:
                access_token = response.payload.get('access_token')
                account = await auth_service.verify_token(access_token)
                
                # Create session for the user
                self._current_session_id, jwt_token = await self._session_manager.create_session(
                    account, 
                    device_info="Trade Buddy SDK",
                    ip_address="localhost"
                )
                
                # Convert to new TBResponse format
                user_data = UserData(**account.model_dump_safe())
                login_data = LoginData(
                    user=user_data,
                    access_token=jwt_token,
                    session_id=self._current_session_id
                )
                return TBResponse(
                    message="Login successful",
                    data=login_data.model_dump()
                )
            else:
                return TBResponse(message=response.message, data=None)
            
        except (ValidationError, AuthenticationError):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Login failed: {str(e)}")
    
    async def create_order(self, data: Dict[str, Any]) -> TBResponse:
        """
        Create new order
        
        Args:
            data: Order data dictionary
            
        Returns:
            TBResponse with order details
        """
        session = await self._require_authentication()
        
        try:
            # Validate input
            if isinstance(data, dict):
                schema = CreateOrderSchema(**data)
            else:
                schema = data
            
            order_service = self._service_factory.create_service('order')
            response = await order_service.create_new_order(session.account, schema)
            
            # Convert to new TBResponse format
            if response.success:
                order_data = OrderData(**response.payload['order'])
                return TBResponse(
                    message="Order created successfully",
                    data={"order": order_data.model_dump()}
                )
            else:
                return TBResponse(message=response.message, data=None)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Order creation failed: {str(e)}")
    
    async def update_stoploss(self, data: Dict[str, Any]) -> TBResponse:
        """Create/update stoploss order"""
        session = await self._require_authentication()
        
        try:
            if isinstance(data, dict):
                schema = UpdateStoplossSchema(**data)
            else:
                schema = data
            
            order_service = self._service_factory.create_service('order')
            response = await order_service.create_stoploss_order(session.account, schema)
            
            # Convert to new TBResponse format
            if response.success:
                order_data = OrderData(**response.payload['order'])
                return TBResponse(
                    message="Stoploss updated successfully",
                    data={"order": order_data.model_dump()}
                )
            else:
                return TBResponse(message=response.message, data=None)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Stoploss update failed: {str(e)}")
    
    async def update_quantity(self, data: Dict[str, Any]) -> TBResponse:
        """Update position quantity"""
        session = await self._require_authentication()
        
        try:
            if isinstance(data, dict):
                schema = UpdateQuantitySchema(**data)
            else:
                schema = data
            
            order_service = self._service_factory.create_service('order')
            response = await order_service.update_quantity(session.account, schema)
            
            # Convert to new TBResponse format
            if response.success:
                order_data = OrderData(**response.payload['order'])
                return TBResponse(
                    message="Quantity updated successfully",
                    data={"order": order_data.model_dump()}
                )
            else:
                return TBResponse(message=response.message, data=None)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Quantity update failed: {str(e)}")
    
    async def exit_position(self, data: Dict[str, Any]) -> TBResponse:
        """Exit position completely"""
        session = await self._require_authentication()
        
        try:
            if isinstance(data, dict):
                schema = ExitOrderSchema(**data)
            else:
                schema = data
            
            order_service = self._service_factory.create_service('order')
            response = await order_service.exit_position(session.account, schema)
            
            # Convert to new TBResponse format
            if response.success:
                position_data = PositionData(**response.payload['position'])
                return TBResponse(
                    message="Position exited successfully",
                    data={"position": position_data.model_dump()}
                )
            else:
                return TBResponse(message=response.message, data=None)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Position exit failed: {str(e)}")
    
    async def get_positions(self) -> TBResponse:
        """Get user positions with overview"""
        session = await self._require_authentication()
        
        try:
            position_service = self._service_factory.create_service('position')
            positions_data = await position_service.get_positions(session.account)
            
            # Convert to new TBResponse format
            overview = PositionsOverview(**positions_data)
            return TBResponse(
                message="Positions retrieved successfully",
                data=overview.model_dump()
            )
            
        except Exception as e:
            raise TradeBuddyException(f"Failed to retrieve positions: {str(e)}")
    
    async def get_position_history(self) -> TBResponse:
        """Get all completed positions"""
        session = await self._require_authentication()
        
        try:
            position_service = self._service_factory.create_service('position')
            positions = await position_service.get_all_positions(session.account)
            
            # Convert to new TBResponse format
            positions_data = [PositionData(**pos.model_dump()) for pos in positions]
            return TBResponse(
                message="Position history retrieved successfully",
                data={"positions": [pos.model_dump() for pos in positions_data]}
            )
            
        except Exception as e:
            raise TradeBuddyException(f"Failed to retrieve position history: {str(e)}")
    
    async def create_transaction(self, data: Dict[str, Any]) -> TBResponse:
        """Create transaction (deposit/withdraw)"""
        session = await self._require_authentication()
        
        try:
            if isinstance(data, dict):
                schema = TransactionSchema(**data)
            else:
                schema = data
            
            transaction_service = self._service_factory.create_service('transaction')
            response = await transaction_service.create_transaction(session.account, schema)
            
            # Convert to new TBResponse format
            if response.success:
                transaction_data = TransactionData(**response.payload['transaction'])
                return TBResponse(
                    message="Transaction created successfully",
                    data={"transaction": transaction_data.model_dump()}
                )
            else:
                return TBResponse(message=response.message, data=None)
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Transaction failed: {str(e)}")
    
    async def get_account_details(self) -> TBResponse:
        """Get current account details"""
        session = await self._require_authentication()
        account_data = AccountData(**session.account.model_dump_safe())
        return TBResponse(
            message="Account details retrieved successfully",
            data={"account": account_data.model_dump()}
        )
    
    def search_symbols(self, query: str) -> TBResponse:
        """Search for stock/option symbols"""
        try:
            price_service = self._service_factory.create_service('price')
            symbols = price_service.search_symbols(query)
            
            # Convert to new TBResponse format
            symbols_data = [SymbolData(**symbol) for symbol in symbols]
            return TBResponse(
                message="Symbols found successfully",
                data={"symbols": [symbol.model_dump() for symbol in symbols_data]}
            )
        except Exception as e:
            raise TradeBuddyException(f"Symbol search failed: {str(e)}")
    
    def get_live_price(self, symbol_id: str, symbol_type: str = "Stocks") -> TBResponse:
        """Get live price for a symbol"""
        try:
            price_service = self._service_factory.create_service('price')
            price_data = price_service.get_stock_price(symbol_id, symbol_type)
            
            if price_data:
                price = PriceData(**price_data)
                return TBResponse(
                    message="Price retrieved successfully",
                    data={"price": price.model_dump()}
                )
            else:
                return TBResponse(
                    message="Symbol not found",
                    data=None
                )
        except Exception as e:
            raise TradeBuddyException(f"Price fetch failed: {str(e)}")
    
    def get_multiple_prices(self, symbols: List[Dict[str, str]]) -> TBResponse:
        """Get live prices for multiple symbols"""
        try:
            price_service = self._service_factory.create_service('price')
            prices = price_service.get_multiple_prices(symbols)
            
            # Convert to new TBResponse format
            prices_data = [PriceData(**price) for price in prices]
            return TBResponse(
                message="Prices retrieved successfully",
                data={"prices": [price.model_dump() for price in prices_data]}
            )
        except Exception as e:
            raise TradeBuddyException(f"Multiple price fetch failed: {str(e)}")
    
    async def send_support_ticket(self, data: Dict[str, Any]) -> TBResponse:
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
            
            ticket_data = TicketData(**ticket.model_dump())
            return TBResponse(
                message="Support ticket created successfully",
                data={"ticket": ticket_data.model_dump()}
            )
            
        except ValidationError:
            raise
        except Exception as e:
            raise TradeBuddyException(f"Failed to create support ticket: {str(e)}")
    
    async def verify_email(self, token: str) -> TBResponse:
        """Verify email with token"""
        try:
            auth_service = self._service_factory.create_service('auth')
            response = await auth_service.verify_email(token)
            
            # Convert to new TBResponse format
            if response.success:
                return TBResponse(
                    message="Email verified successfully",
                    data={"verified": True}
                )
            else:
                return TBResponse(message=response.message, data={"verified": False})
            
        except (ValidationError, AuthenticationError):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Email verification failed: {str(e)}")
    
    async def logout(self) -> TBResponse:
        """Logout current user"""
        if self._current_session_id:
            await self._session_manager.destroy_session(self._current_session_id)
            self._current_session_id = None
        
        return TBResponse(
            message="Logout successful",
            data={"logged_out": True}
        )
    
    # Additional utility methods
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        if not self._current_session_id:
            return False
        
        # Use asyncio to handle the async session manager
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return False  # Cannot validate in running loop context
            return loop.run_until_complete(self._session_manager.validate_session(self._current_session_id))
        except:
            return False
    
    async def get_current_balance(self) -> float:
        """Get current account balance"""
        session = await self._require_authentication()
        return session.account.balance
    
    async def delete_account(self, account_id: str) -> TBResponse:
        """
        Delete account and all associated data
        
        Args:
            account_id: Account ID to delete
            
        Returns:
            TBResponse confirming deletion
        """
        try:
            await self._initialize_database()
            db_manager = get_database_manager()
            await db_manager.clear_account_data(account_id)
            
            # If current account is being deleted, logout
            if self._current_session_id:
                session = await self._session_manager.get_session(self._current_session_id)
                if session and session.account.account_id == account_id:
                    await self.logout()
            
            return TBResponse(
                message="Account and all associated data deleted successfully",
                data={"account_id": account_id, "deleted": True}
            )
            
        except Exception as e:
            raise TradeBuddyException(f"Failed to delete account: {str(e)}")
    
    async def clear(self) -> TBResponse:
        """
        Clear entire database - truncate all tables and entities
        
        Returns:
            TBResponse confirming database clear
        """
        try:
            await self._initialize_database()
            db_manager = get_database_manager()
            await db_manager.truncate_all_tables()
            
            # Clear all sessions
            await self._session_manager.clear_all_sessions()
            self._current_session_id = None
            
            return TBResponse(
                message="Database cleared successfully - all tables truncated",
                data={"cleared": True}
            )
            
        except Exception as e:
            raise TradeBuddyException(f"Failed to clear database: {str(e)}")
    
    async def clear_all_data(self):
        """Clear all data (for testing purposes only) - Legacy method"""
        repo_factory = self._service_factory.get_repository_factory()
        repo_factory.clear_all_repositories()
        await self._session_manager.clear_all_sessions()
        self._current_session_id = None
    
    async def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information"""
        if not self._current_session_id:
            return None
        
        return await self._session_manager.get_session_info(self._current_session_id)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions (admin feature)"""
        return self._session_manager.get_active_sessions_count()
    
    async def validate_token(self, token: str) -> TBResponse:
        """Validate JWT token manually"""
        try:
            auth_service = self._service_factory.create_service('auth')
            account = await auth_service.verify_token(token)
            
            if account:
                return TBResponse(
                    message="Token is valid",
                    data={
                        "valid": True,
                        "account_id": account.account_id,
                        "email": account.email_id
                    }
                )
            else:
                return TBResponse(
                    message="Invalid token",
                    data={"valid": False}
                )
                
        except AuthenticationError as e:
            return TBResponse(
                message=str(e),
                data={"valid": False}
            )