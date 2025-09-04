"""
Main broker class - Production ready Trade Buddy SDK with Database Integration
"""

import asyncio
from typing import Optional, List, Dict, Any

from trade_buddy.entities.models import Account
from trade_buddy.entities.schemas import (
    RegistrationSchema, LoginSchema, TransactionSchema
)
from trade_buddy.entities.response_schemas import (
    UserData, LoginData, TransactionData, AccountData,
    SymbolData, PriceData
)
from trade_buddy.core.exceptions import AuthenticationError, ValidationError, TradeBuddyException
from trade_buddy.core.response import TBResponse
from trade_buddy.core.database import get_database_manager, initialize_database
from trade_buddy.core.session_manager import DatabaseSessionManager
from trade_buddy.services.auth_service import AuthService
from trade_buddy.services.transaction_service import TransactionService
from trade_buddy.services.price_service import PriceService
from trade_buddy.services.position_service import PositionService
from typing import Optional, List, Dict, Any


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
        
        # Create transaction
        response = await broker.create_transaction(transaction_data)
    """
    
    def __init__(self):
        """Initialize Trade Buddy broker"""
        # Initialize basic properties first
        self._current_session_id: Optional[str] = None
        self._initialized = False
        self._db_initialized = False
        self.test = "Test By jay"
        
        # Initialize services with lazy loading
        self._auth_service = None
        self._transaction_service = None
        self._price_service = None
        self._session_manager = None
        self._position_service = None
    
    def _get_auth_service(self):
        if self._auth_service is None:
            self._auth_service = AuthService()
        return self._auth_service
    
    def _get_transaction_service(self):
        if self._transaction_service is None:
            self._transaction_service = TransactionService()
        return self._transaction_service
    
    def _get_price_service(self):
        if self._price_service is None:
            self._price_service = PriceService()
        return self._price_service
    
    def _get_position_service(self):
        if self._position_service is None:
            self._position_service = PositionService()
        return self._position_service
    
    def _get_session_manager(self):
        """Get session manager with lazy initialization - only when needed"""
        if self._session_manager is None:
            self._session_manager = DatabaseSessionManager()
        return self._session_manager
    
    # Quick access properties for basic usage
    # Backward-compatibility shims removed
        
    @property  
    def session_manager(self):
        """Property access to session manager (may be slow on first access)"""
        return self._get_session_manager()
    
    async def _initialize_database(self):
        """Initialize database tables"""
        if not self._db_initialized:
            try:
                await initialize_database()
                self._db_initialized = True
            except Exception as e:
                raise TradeBuddyException(f"Database initialization failed: {e}")
    
    async def _initialize_demo_data(self):
        """Initialize with demo account"""
        if self._initialized:
            return
        
        try:
            auth_service = self._get_auth_service()
            
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
            
            from trade_buddy.repositories.account_repository import AccountRepository
            account_repo = AccountRepository()
            
            try:
                await account_repo.create(demo_account)
            except TradeBuddyException:
                pass  # Account already exists
            
            self._initialized = True
            
        except Exception:
            pass  # Silent fail for demo data
    
    async def _require_authentication(self) -> Dict[str, Any]:
        """Check if user is authenticated and return session"""
        if not self._current_session_id:
            raise AuthenticationError("Please login first")
        
        session_data = await self._get_session_manager().get_session(self._current_session_id)
        if not session_data:
            raise AuthenticationError("Session expired, please login again")
        
        # Validate session token
        if not await self._get_session_manager().validate_session(self._current_session_id):
            raise AuthenticationError("Invalid session, please login again")
        
        return session_data
    
    async def _get_account_from_session(self) -> Account:
        """Get account from current session"""
        session_data = await self._require_authentication()
        
        # Get account from session data
        from trade_buddy.repositories import AccountRepository
        account_repo = AccountRepository()
        account = await account_repo.get_by_id(session_data['account_id'])
        if not account:
            raise AuthenticationError("Account not found")
        
        return account
    
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
            
            auth_service = self._get_auth_service()
            response = await auth_service.register(schema)
            # Pass through in unified TBResponse shape
            return response
            
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
            
            auth_service = self._get_auth_service()
            response = await auth_service.login(schema)
            
            # Store session
            if response.data:
                access_token = response.data.get('access_token')
                account = await auth_service.verify_token(access_token)
                
                # Create session for the user
                self._current_session_id, jwt_token = await self._get_session_manager().create_session(
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
    
    async def create_transaction(self, data: Dict[str, Any]) -> TBResponse:
        """Create transaction (deposit/withdraw)"""
        account = await self._get_account_from_session()
        
        try:
            if isinstance(data, dict):
                schema = TransactionSchema(**data)
            else:
                schema = data
            
            transaction_service = self._get_transaction_service()
            response = await transaction_service.create_transaction(account, schema)
            return response
            
        except (ValidationError, TradeBuddyException):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Transaction failed: {str(e)}")
    
    async def get_account_details(self) -> TBResponse:
        """Get current account details"""
        account = await self._get_account_from_session()
        account_data = AccountData(**account.model_dump_safe())
        return TBResponse(
            message="Account details retrieved successfully",
            data={"account": account_data.model_dump()}
        )
    
    def search_symbols(self, query: str) -> TBResponse:
        """Search for stock/option symbols"""
        try:
            price_service = self._get_price_service()
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
            price_service = self._get_price_service()
            price_data = price_service.get_stock_price(symbol_id, symbol_type)
            
            if price_data:
                mapped = {
                    "symbol_id": price_data.get("id", symbol_id),
                    "symbol_type": price_data.get("type", symbol_type),
                    "ltp": price_data.get("ltp"),
                    "open_price": price_data.get("open") or price_data.get("open_price"),
                    "high_price": price_data.get("high") or price_data.get("high_price"),
                    "low_price": price_data.get("low") or price_data.get("low_price"),
                    "prev_close": price_data.get("close") or price_data.get("prev_close"),
                    "change": price_data.get("change"),
                    "change_percent": price_data.get("changePercent") or price_data.get("change_percent"),
                }
                price = PriceData(**mapped)
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
            price_service = self._get_price_service()
            raw_prices = price_service.get_multiple_prices(symbols)
            
            # Convert to new TBResponse format
            prices_data = []
            for price in raw_prices:
                mapped = {
                    "symbol_id": price.get("id") or price.get("symbol_id"),
                    "symbol_type": price.get("type") or price.get("symbol_type"),
                    "ltp": price.get("ltp"),
                    "open_price": price.get("open") or price.get("open_price"),
                    "high_price": price.get("high") or price.get("high_price"),
                    "low_price": price.get("low") or price.get("low_price"),
                    "prev_close": price.get("close") or price.get("prev_close"),
                    "change": price.get("change"),
                    "change_percent": price.get("changePercent") or price.get("change_percent"),
                }
                prices_data.append(PriceData(**mapped))
            return TBResponse(
                message="Prices retrieved successfully",
                data={"prices": [price.model_dump() for price in prices_data]}
            )
        except Exception as e:
            raise TradeBuddyException(f"Multiple price fetch failed: {str(e)}")

    # Position APIs
    async def open_position(self, symbol_id: str, quantity: int, price: float, side: str, stoploss: float | None = None, target: float | None = None) -> TBResponse:
        account = await self._get_account_from_session()
        try:
            pos = self._get_position_service().open_position(account, symbol_id, quantity, price, side, stoploss, target)
            return TBResponse(message="Position opened", data={"position": pos})
        except Exception as e:
            raise TradeBuddyException(f"Open position failed: {str(e)}")

    async def update_position_levels(self, position_id: str, stoploss: float | None = None, target: float | None = None) -> TBResponse:
        account = await self._get_account_from_session()
        try:
            pos = self._get_position_service().update_levels(account, position_id, stoploss, target)
            return TBResponse(message="Position levels updated", data={"position": pos})
        except Exception as e:
            raise TradeBuddyException(f"Update levels failed: {str(e)}")

    async def exit_position(self, position_id: str, exit_price: float) -> TBResponse:
        account = await self._get_account_from_session()
        try:
            pos = self._get_position_service().exit_position(account, position_id, exit_price)
            return TBResponse(message="Position exited", data={"position": pos})
        except Exception as e:
            raise TradeBuddyException(f"Exit position failed: {str(e)}")

    async def get_open_positions(self) -> TBResponse:
        account = await self._get_account_from_session()
        positions = self._get_position_service().get_open_positions(account.account_id)
        return TBResponse(message="Open positions", data={"positions": positions})

    async def get_position_history(self) -> TBResponse:
        account = await self._get_account_from_session()
        positions = self._get_position_service().get_position_history(account.account_id)
        return TBResponse(message="Position history", data={"positions": positions})
    
    async def verify_email(self, token: str) -> TBResponse:
        """Verify email with token"""
        try:
            auth_service = self._get_auth_service()
            response = await auth_service.verify_email(token)
            return response
            
        except (ValidationError, AuthenticationError):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Email verification failed: {str(e)}")
    
    async def logout(self) -> TBResponse:
        """Logout current user"""
        if self._current_session_id:
            await self._get_session_manager().destroy_session(self._current_session_id)
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
            return loop.run_until_complete(self._get_session_manager().validate_session(self._current_session_id))
        except:
            return False
    
    async def get_current_balance(self) -> float:
        """Get current account balance"""
        account = await self._get_account_from_session()
        return account.balance
    
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
                session_data = await self._get_session_manager().get_session(self._current_session_id)
                if session_data and session_data['account_id'] == account_id:
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
            await self._get_session_manager().clear_all_sessions()
            self._current_session_id = None
            return TBResponse(message="Database cleared successfully - all tables truncated", data={"cleared": True})
            
        except Exception as e:
            raise TradeBuddyException(f"Failed to clear database: {str(e)}")
    
    async def clear_all_data(self):
        """Clear all data (for testing purposes only) - Legacy method"""
        # No repository factory; nothing to clear in memory here
        await self._get_session_manager().clear_all_sessions()
        self._current_session_id = None

    # Background helpers removed
    
    async def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information"""
        if not self._current_session_id:
            return None
        
        return await self._get_session_manager().get_session_info(self._current_session_id)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions (admin feature)"""
        return self._get_session_manager().get_active_sessions_count()
    
    async def validate_token(self, token: str) -> TBResponse:
        """Validate JWT token manually"""
        try:
            auth_service = self._get_auth_service()
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