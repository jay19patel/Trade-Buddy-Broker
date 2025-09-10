"""
Main broker class - Production ready Trade Buddy SDK with Database Integration
"""

import asyncio
from typing import Optional, Dict, Any

from trade_buddy.entities.models import Account
from trade_buddy.entities.schemas import (
    RegistrationSchema, LoginSchema, TransactionSchema
)
from trade_buddy.entities.response_schemas import (
    UserData, LoginData, AccountData
)
from trade_buddy.core.exceptions import AuthenticationError, ValidationError, TradeBuddyException
from trade_buddy.core.response import TBResponse
from trade_buddy.core.database import get_database_manager, initialize_database
from trade_buddy.core.session_manager import DatabaseSessionManager
from trade_buddy.services.auth_service import AuthService
from trade_buddy.services.transaction_service import TransactionService
from trade_buddy.services.position_service import PositionService
from trade_buddy.services.notification_service import NotificationService
from trade_buddy.patterns.observer import get_caller_info


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
        self._current_session_id: Optional[str] = None
        self._initialized = False
        self._db_initialized = False
        
        # Initialize services with lazy loading
        self._auth_service = None
        self._transaction_service = None
        self._session_manager = None
        self._position_service = None
        self._notification_service = None
    
    def _get_auth_service(self):
        if self._auth_service is None:
            self._auth_service = AuthService()
        return self._auth_service
    
    def _get_transaction_service(self):
        if self._transaction_service is None:
            self._transaction_service = TransactionService()
        return self._transaction_service
    
    
    def _get_position_service(self):
        if self._position_service is None:
            self._position_service = PositionService()
        return self._position_service
    
    def _get_notification_service(self):
        if self._notification_service is None:
            self._notification_service = NotificationService()
        return self._notification_service
    
    def _get_session_manager(self):
        """Get session manager with lazy initialization - only when needed"""
        if self._session_manager is None:
            self._session_manager = DatabaseSessionManager()
        return self._session_manager
    
    @property  
    def session_manager(self):
        """Property access to session manager"""
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
            
            demo_balance = 100000.0
            demo_account = Account(
                account_id="DEMO01",
                full_name="Demo User",
                email_id="demo@tradebuddy.com",
                password=security.generate_hash_password("demo123"),
                balance=demo_balance,
                email_verified=True,
                description="Demo account for testing",
                default_leverage=1.0,
                total_margin=0.0,
                utilized_margin=0.0,
                available_margin=demo_balance,
                margin_percentage=0.0
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

    # Public helper to fetch current Account once after login
    async def get_account(self) -> Account:
        return await self._get_account_from_session()
    
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
                # Include account object and serialized account for downstream use
                data = login_data.model_dump()
                data.update({
                    "account": account.model_dump_safe(),
                    "account_obj": account
                })
                return TBResponse(message="Login successful", data=data)
            else:
                return TBResponse(message=response.message, data=None)
            
        except (ValidationError, AuthenticationError):
            raise
        except Exception as e:
            raise TradeBuddyException(f"Login failed: {str(e)}")
    
    async def create_transaction(self, account: Account, data: Dict[str, Any]) -> TBResponse:
        """Create transaction (deposit/withdraw)"""
        
        try:
            if isinstance(data, dict):
                schema = TransactionSchema(**data)
            else:
                schema = data
            
            transaction_service = self._get_transaction_service()
            response = await transaction_service.create_transaction(account, schema)
            
            # Notify observers about transaction creation
            if response.data and response.data.get("transaction"):
                notification_service = self._get_notification_service()
                await notification_service.notify("transaction_created", {
                    "account_id": account.account_id,
                    "transaction": response.data["transaction"]
                })
            
            return response
            
        except (ValidationError, TradeBuddyException):
            # Notify observers about error
            try:
                notification_service = self._get_notification_service()
                caller_info = get_caller_info()
                await notification_service.notify("error_occurred", {
                    "account_id": account.account_id,
                    "error": TradeBuddyException(f"Transaction validation failed"),
                    "function_name": caller_info["function_name"],
                    "class_name": caller_info["class_name"],
                    "file_name": caller_info["file_name"]
                })
            except:
                pass  # Don't let notification errors break the main flow
            raise
        except Exception as e:
            # Notify observers about error
            try:
                notification_service = self._get_notification_service()
                caller_info = get_caller_info()
                await notification_service.notify("error_occurred", {
                    "account_id": account.account_id,
                    "error": e,
                    "function_name": caller_info["function_name"],
                    "class_name": caller_info["class_name"],
                    "file_name": caller_info["file_name"]
                })
            except:
                pass  # Don't let notification errors break the main flow
            raise TradeBuddyException(f"Transaction failed: {str(e)}")
    
    async def get_account_details(self, account: Account) -> TBResponse:
        """Get current account details with updated margin calculations"""
        # Refresh account from database to get latest margin values
        try:
            from trade_buddy.repositories.account_repository import AccountRepository
            acc_repo = AccountRepository()
            fresh_account = await acc_repo.get_by_id(account.account_id)
            if fresh_account:
                account = fresh_account
        except Exception:
            pass
        
        # Ensure margin stats are properly calculated
        utilized_margin = getattr(account, "utilized_margin", 0.0)
        balance = getattr(account, "balance", 0.0)
        available_margin = max(balance - utilized_margin, 0.0)
        margin_percentage = (utilized_margin / balance * 100) if balance > 0 else 0.0
        
        account_payload = account.model_dump_safe()
        account_payload.update({
            "total_margin": max(getattr(account, "total_margin", 0.0), utilized_margin),
            "utilized_margin": utilized_margin,
            "available_margin": available_margin,
            "margin_percentage": margin_percentage,
            "default_leverage": getattr(account, "default_leverage", 1.0),
        })
        account_data = AccountData(**account_payload)
        return TBResponse(
            message="Account details retrieved successfully",
            data={"account": account_data.model_dump()}
        )
    
    
    

    # Position APIs
    async def open_position(self, account: Account, symbol_id: str, remaining_quantity: int, price: float, side: str, stoploss: float | None = None, target: float | None = None) -> TBResponse:
        try:
            pos = await self._get_position_service().open_position(account, symbol_id, remaining_quantity, price, side, stoploss, target)
            
            # Notify observers about position opened
            notification_service = self._get_notification_service()
            await notification_service.notify("position_opened", {
                "account_id": account.account_id,
                "position": pos
            })
            
            return TBResponse(message="Position opened successfully", data={"position": pos.model_dump()})
        except ValueError as e:
            # Return user-friendly error for insufficient funds
            return TBResponse(message=str(e), data=None)
        except Exception as e:
            # Notify observers about error
            try:
                notification_service = self._get_notification_service()
                caller_info = get_caller_info()
                await notification_service.notify("error_occurred", {
                    "account_id": account.account_id,
                    "error": e,
                    "function_name": caller_info["function_name"],
                    "class_name": caller_info["class_name"],
                    "file_name": caller_info["file_name"]
                })
            except:
                pass
            raise TradeBuddyException(f"Open position failed: {str(e)}")


    async def exit_position(self, account: Account, position_id: str, exit_price: float, close_quantity: float | None = None) -> TBResponse:
        try:
            if close_quantity is not None and close_quantity > 0:
                pos = await self._get_position_service().partial_close(account, position_id, close_quantity, exit_price)
            else:
                pos = await self._get_position_service().exit_position(account, position_id, exit_price)

            # Notify observers about position closed/partial
            notification_service = self._get_notification_service()
            event_name = "position_closed" if getattr(pos, "status", None) == "CLOSED" else "position_trailed"
            payload = {
                "account_id": account.account_id,
                "position": pos
            }
            if close_quantity is not None and close_quantity > 0:
                payload.update({"close_quantity": close_quantity, "exit_price": exit_price})
            await notification_service.notify(event_name, payload)

            return TBResponse(message="Position exited successfully" if event_name == "position_closed" else "Partial exit applied successfully", data={"position": pos.model_dump()})
        except ValueError as e:
            # Return user-friendly error
            return TBResponse(message=str(e), data=None)
        except Exception as e:
            # Notify observers about error
            try:
                notification_service = self._get_notification_service()
                caller_info = get_caller_info()
                await notification_service.notify("error_occurred", {
                    "account_id": account.account_id,
                    "error": e,
                    "function_name": caller_info["function_name"],
                    "class_name": caller_info["class_name"],
                    "file_name": caller_info["file_name"]
                })
            except:
                pass
            raise TradeBuddyException(f"Exit position failed: {str(e)}")

    async def get_open_positions(self, account: Account) -> TBResponse:
        positions = await self._get_position_service().get_open_positions(account.account_id)
        return TBResponse(message="Open positions", data={"positions": [p.model_dump() for p in positions]})

    async def get_position_history(self, account: Account) -> TBResponse:
        positions = await self._get_position_service().get_position_history(account.account_id)
        return TBResponse(message="Position history", data={"positions": [p.model_dump() for p in positions]})

    async def get_transaction_history(self, account: Account) -> TBResponse:
        """Get transaction history for account"""
        try:
            transaction_service = self._get_transaction_service()
            transactions = await transaction_service.get_transaction_history(account)
            return TBResponse(
                message="Transaction history retrieved successfully",
                data={"transactions": transactions}
            )
        except Exception as e:
            raise TradeBuddyException(f"Failed to fetch transaction history: {str(e)}")

    # Advanced
    async def pyramid(self, account: Account, position_id: str, additional_quantity: float, new_price: float) -> TBResponse:
        try:
            pos = await self._get_position_service().add_to_position(account, position_id, additional_quantity, new_price)
            
            # Notify observers about position pyramided
            notification_service = self._get_notification_service()
            await notification_service.notify("position_pyramided", {
                "account_id": account.account_id,
                "position": pos,
                "additional_quantity": additional_quantity,
                "new_price": new_price
            })
            
            return TBResponse(message="Pyramiding applied successfully", data={"position": pos.model_dump()})
        except ValueError as e:
            # Return user-friendly error for insufficient funds
            return TBResponse(message=str(e), data=None)
        except Exception as e:
            # Notify observers about error
            try:
                notification_service = self._get_notification_service()
                caller_info = get_caller_info()
                await notification_service.notify("error_occurred", {
                    "account_id": account.account_id,
                    "error": e,
                    "function_name": caller_info["function_name"],
                    "class_name": caller_info["class_name"],
                    "file_name": caller_info["file_name"]
                })
            except:
                pass
            raise TradeBuddyException(f"Pyramiding failed: {str(e)}")

    async def trailing(self, account: Account, position_id: str, close_quantity: float, exit_price: float, stoploss: float | None = None, target: float | None = None) -> TBResponse:
        try:
            # Always update levels when provided; trailing feature flag removed
            if stoploss is not None or target is not None:
                await self._get_position_service().update_levels(account, position_id, stoploss, target)
            pos = await self._get_position_service().partial_close(account, position_id, close_quantity, exit_price)
            
            # Notify observers about position trailed
            notification_service = self._get_notification_service()
            await notification_service.notify("position_trailed", {
                "account_id": account.account_id,
                "position": pos,
                "close_quantity": close_quantity,
                "exit_price": exit_price
            })
            
            return TBResponse(message="Trailing partial exit applied", data={"position": pos.model_dump()})
        except Exception as e:
            # Notify observers about error
            try:
                notification_service = self._get_notification_service()
                caller_info = get_caller_info()
                await notification_service.notify("error_occurred", {
                    "account_id": account.account_id,
                    "error": e,
                    "function_name": caller_info["function_name"],
                    "class_name": caller_info["class_name"],
                    "file_name": caller_info["file_name"]
                })
            except:
                pass
            raise TradeBuddyException(f"Trailing failed: {str(e)}")

    async def update_position_levels(self, account: Account, position_id: str, stoploss: float | None = None, target: float | None = None) -> TBResponse:
        """Update position stop loss and target levels"""
        try:
            pos = await self._get_position_service().update_levels(account, position_id, stoploss, target)
            
            # Notify observers about position updated
            changes = {}
            if stoploss is not None:
                changes["stoploss"] = stoploss
            if target is not None:
                changes["target"] = target
                
            notification_service = self._get_notification_service()
            await notification_service.notify("position_updated", {
                "account_id": account.account_id,
                "position": pos,
                "changes": changes
            })
            
            return TBResponse(message="Position levels updated", data={"position": pos.model_dump()})
        except Exception as e:
            # Notify observers about error
            try:
                notification_service = self._get_notification_service()
                caller_info = get_caller_info()
                await notification_service.notify("error_occurred", {
                    "account_id": account.account_id,
                    "error": e,
                    "function_name": caller_info["function_name"],
                    "class_name": caller_info["class_name"],
                    "file_name": caller_info["file_name"]
                })
            except:
                pass
            raise TradeBuddyException(f"Update levels failed: {str(e)}")

    async def update_leverage(self, account: Account, leverage: float) -> TBResponse:
        try:
            if leverage <= 0:
                raise ValidationError("Leverage must be > 0")
            # Persist on account model (in-memory repo in this flow)
            from trade_buddy.repositories import AccountRepository
            repo = AccountRepository()
            old_leverage = account.default_leverage
            account.default_leverage = leverage
            await repo.update(account)
            
            # Notify observers about leverage updated
            notification_service = self._get_notification_service()
            await notification_service.notify("leverage_updated", {
                "account_id": account.account_id,
                "old_leverage": old_leverage,
                "new_leverage": leverage
            })
            
            return TBResponse(message="Default leverage updated", data={"leverage": leverage})
        except Exception as e:
            # Notify observers about error
            try:
                notification_service = self._get_notification_service()
                caller_info = get_caller_info()
                await notification_service.notify("error_occurred", {
                    "account_id": account.account_id,
                    "error": e,
                    "function_name": caller_info["function_name"],
                    "class_name": caller_info["class_name"],
                    "file_name": caller_info["file_name"]
                })
            except:
                pass
            raise TradeBuddyException(f"Update leverage failed: {str(e)}")

    
    
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
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return bool(self._current_session_id)
    
    
    # Notification APIs
    async def get_notifications(self, account: Account, limit: int = 50) -> TBResponse:
        """Get notifications for account"""
        notification_service = self._get_notification_service()
        return await notification_service.get_notifications(account.account_id, limit)
    
    async def get_notifications_by_type(self, account: Account, notification_type: str, limit: int = 20) -> TBResponse:
        """Get notifications by type for account"""
        notification_service = self._get_notification_service()
        return await notification_service.get_notifications_by_type(account.account_id, notification_type, limit)
    
    async def delete_notification(self, notification_id: str) -> TBResponse:
        """Delete notification"""
        notification_service = self._get_notification_service()
        return await notification_service.delete_notification(notification_id)
    
    # New subscription-style APIs
    # Simplified notifications API
    def notification_set_email(self, config: Dict[str, Any]) -> None:
        notification_service = self._get_notification_service()
        notification_service.set_email_config(config)

    async def read_notification(self, notification_id: str) -> TBResponse:
        """Mark notification as read (sent) in DB"""
        notification_service = self._get_notification_service()
        return await notification_service.mark_notification_sent(notification_id)

    async def get_notifications_paginated(self, account: Account, page: int = 1, page_size: int = 20) -> TBResponse:
        notification_service = self._get_notification_service()
        return await notification_service.get_notifications_paginated(account.account_id, page, page_size)
    
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
        """Clear all data (for testing purposes only)"""
        await self._get_session_manager().clear_all_sessions()
        self._current_session_id = None
    
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