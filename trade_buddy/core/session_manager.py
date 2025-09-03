"""
Production-Grade Hybrid Session Manager
- Database persistence for audit & security
- In-memory cache for performance
- JWT tokens for API compatibility
- Multi-user support with cleanup
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import threading
from sqlalchemy import select, update, delete

from trade_buddy.entities.models import Account, Session
from trade_buddy.utils.security import SecurityManager
from trade_buddy.utils.singleton import Singleton
from trade_buddy.core.database import get_database_manager


class SessionData:
    """In-memory session data for fast access"""
    
    def __init__(self, session_id: str, account: Account, jwt_token: str, expires_at: datetime):
        self.session_id = session_id
        self.account = account
        self.jwt_token = jwt_token
        self.expires_at = expires_at
        self.last_activity = datetime.now()
        self.created_at = datetime.now()
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.now() > self.expires_at
    
    def is_inactive(self, inactive_minutes: int = 30) -> bool:
        """Check if session is inactive"""
        inactive_time = self.last_activity + timedelta(minutes=inactive_minutes)
        return datetime.now() > inactive_time


class HybridSessionManager(Singleton):
    """
    Production-Ready Hybrid Session Manager
    
    Features:
    🔄 Database + Memory hybrid storage
    🔑 JWT token integration
    👥 Multi-user session management
    🧹 Automatic cleanup & expiry
    🚀 High-performance caching
    🔒 Security audit trail
    📊 Session analytics
    
    Perfect for API integration & production use
    """
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            # In-memory cache for fast access
            self._memory_sessions: Dict[str, SessionData] = {}
            self._account_sessions: Dict[str, str] = {}  # account_id -> session_id
            
            # Thread safety
            self._lock = threading.RLock()
            
            # Components
            self._security = SecurityManager()
            self._db_manager = get_database_manager()
            
            # Configuration
            self.token_expiry_hours = 24
            self.inactive_timeout_minutes = 30
            self.cleanup_interval_minutes = 15
            
            self.initialized = True
    
    async def create_session(
        self, 
        account: Account, 
        device_info: Optional[str] = None, 
        ip_address: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Create new session with database persistence
        
        Args:
            account: User account
            device_info: Optional device information
            ip_address: Optional IP address
            
        Returns:
            Tuple of (session_id, jwt_token)
        """
        with self._lock:
            # Generate session ID and JWT token
            session_id = self._security.generate_unique_id("SESSION")
            
            # Create JWT token with session info
            token_payload = {
                "AccountId": account.account_id,
                "AccountEmail": account.email_id,
                "AccountRole": account.role,
                "SessionId": session_id
            }
            
            expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)
            jwt_token = self._security.create_access_token(
                payload=token_payload,
                expiry=timedelta(hours=self.token_expiry_hours)
            )
            
            # Remove existing session for this account
            await self._cleanup_account_sessions(account.account_id)
            
            # Create database session record
            await self._create_db_session(
                session_id, account.account_id, jwt_token, 
                device_info, ip_address, expires_at
            )
            
            # Store in memory cache
            session_data = SessionData(session_id, account, jwt_token, expires_at)
            self._memory_sessions[session_id] = session_data
            self._account_sessions[account.account_id] = session_id
            
            return session_id, jwt_token
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session with hybrid lookup (Memory -> Database)
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData or None if not found/expired
        """
        with self._lock:
            # First check memory cache
            session = self._memory_sessions.get(session_id)
            
            if session:
                if session.is_expired():
                    await self._cleanup_session(session_id)
                    return None
                
                session.update_activity()
                await self._update_db_activity(session_id)
                return session
            
            # Fallback to database
            return await self._load_session_from_db(session_id)
    
    async def get_session_by_account(self, account_id: str) -> Optional[SessionData]:
        """Get session by account ID"""
        with self._lock:
            session_id = self._account_sessions.get(account_id)
            if session_id:
                return await self.get_session(session_id)
            
            # Check database
            return await self._load_account_session_from_db(account_id)
    
    async def validate_session(self, session_id: str) -> bool:
        """
        Validate session with JWT token verification
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if valid, False otherwise
        """
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Validate JWT token
        try:
            payload = self._security.decode_token(session.jwt_token)
            return payload.get("SessionId") == session_id
        except:
            await self._cleanup_session(session_id)
            return False
    
    async def validate_jwt_token(self, jwt_token: str) -> Optional[SessionData]:
        """
        Validate JWT token and return session
        
        Args:
            jwt_token: JWT token
            
        Returns:
            SessionData or None if invalid
        """
        try:
            payload = self._security.decode_token(jwt_token)
            session_id = payload.get("SessionId")
            
            if session_id:
                session = await self.get_session(session_id)
                if session and session.jwt_token == jwt_token:
                    return session
            
            return None
        except:
            return None
    
    async def destroy_session(self, session_id: str) -> bool:
        """
        Destroy session (logout)
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was destroyed
        """
        with self._lock:
            return await self._cleanup_session(session_id)
    
    async def destroy_account_sessions(self, account_id: str) -> int:
        """
        Destroy all sessions for an account
        
        Args:
            account_id: Account identifier
            
        Returns:
            Number of sessions destroyed
        """
        return await self._cleanup_account_sessions(account_id)
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of all active sessions"""
        await self.cleanup_expired_sessions()
        
        sessions = []
        for session_data in self._memory_sessions.values():
            sessions.append({
                "session_id": session_data.session_id,
                "account_id": session_data.account.account_id,
                "email": session_data.account.email_id,
                "full_name": session_data.account.full_name,
                "created_at": session_data.created_at.isoformat(),
                "last_activity": session_data.last_activity.isoformat(),
                "expires_at": session_data.expires_at.isoformat()
            })
        
        return sessions
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "account_id": session.account.account_id,
            "email": session.account.email_id,
            "full_name": session.account.full_name,
            "balance": session.account.balance,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "expires_at": session.expires_at.isoformat()
        }
    
    async def cleanup_expired_sessions(self) -> int:
        """Cleanup expired and inactive sessions"""
        cleaned_count = 0
        
        # Clean memory sessions
        with self._lock:
            expired_sessions = []
            for session_id, session in self._memory_sessions.items():
                if session.is_expired() or session.is_inactive(self.inactive_timeout_minutes):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                await self._cleanup_session(session_id)
                cleaned_count += 1
        
        # Clean database sessions
        await self._db_manager.cleanup_expired_sessions()
        
        return cleaned_count
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions in memory"""
        return len(self._memory_sessions)
    
    async def clear_all_sessions(self):
        """Clear all sessions (admin/testing purposes)"""
        with self._lock:
            self._memory_sessions.clear()
            self._account_sessions.clear()
            
            # Clear database sessions
            async for db_session in self._db_manager.get_session():
                try:
                    await db_session.execute(delete(Session))
                    await db_session.commit()
                    break
                except Exception as e:
                    await db_session.rollback()
                    raise e
    
    # Private methods
    async def _create_db_session(
        self, session_id: str, account_id: str, jwt_token: str,
        device_info: Optional[str], ip_address: Optional[str], expires_at: datetime
    ):
        """Create session record in database"""
        async for db_session in self._db_manager.get_session():
            try:
                db_session_obj = Session(
                    session_id=session_id,
                    account_id=account_id,
                    jwt_token=jwt_token,
                    device_info=device_info,
                    ip_address=ip_address,
                    expires_at=expires_at,
                    is_active=True
                )
                
                db_session.add(db_session_obj)
                await db_session.commit()
                break
            except Exception as e:
                await db_session.rollback()
                raise e
    
    async def _update_db_activity(self, session_id: str):
        """Update last activity in database"""
        async for db_session in self._db_manager.get_session():
            try:
                await db_session.execute(
                    update(Session)
                    .where(Session.session_id == session_id)
                    .values(last_activity=datetime.now())
                )
                await db_session.commit()
                break
            except Exception:
                await db_session.rollback()
    
    async def _load_session_from_db(self, session_id: str) -> Optional[SessionData]:
        """Load session from database to memory cache"""
        async for db_session in self._db_manager.get_session():
            try:
                stmt = select(Session).where(
                    Session.session_id == session_id,
                    Session.is_active == True
                )
                result = await db_session.execute(stmt)
                db_session_obj = result.scalar_one_or_none()
                
                if db_session_obj and db_session_obj.expires_at > datetime.now():
                    # Load account
                    from trade_buddy.repositories import AccountRepository
                    account_repo = AccountRepository()
                    account = await account_repo.get_by_id(db_session_obj.account_id)
                    
                    if account:
                        # Cache in memory
                        session_data = SessionData(
                            session_id, account, db_session_obj.jwt_token, 
                            db_session_obj.expires_at
                        )
                        session_data.last_activity = db_session_obj.last_activity
                        
                        self._memory_sessions[session_id] = session_data
                        self._account_sessions[account.account_id] = session_id
                        
                        return session_data
                
                return None
                
            except Exception:
                return None
    
    async def _load_account_session_from_db(self, account_id: str) -> Optional[SessionData]:
        """Load account session from database"""
        async for db_session in self._db_manager.get_session():
            try:
                stmt = select(Session).where(
                    Session.account_id == account_id,
                    Session.is_active == True
                )
                result = await db_session.execute(stmt)
                db_session_obj = result.scalar_one_or_none()
                
                if db_session_obj:
                    return await self._load_session_from_db(db_session_obj.session_id)
                
                return None
            except Exception:
                return None
    
    async def _cleanup_session(self, session_id: str) -> bool:
        """Internal cleanup of single session"""
        # Remove from memory
        session = self._memory_sessions.pop(session_id, None)
        if session:
            self._account_sessions.pop(session.account.account_id, None)
        
        # Remove from database
        async for db_session in self._db_manager.get_session():
            try:
                await db_session.execute(
                    update(Session)
                    .where(Session.session_id == session_id)
                    .values(is_active=False)
                )
                await db_session.commit()
                break
            except Exception:
                await db_session.rollback()
        
        return session is not None
    
    async def _cleanup_account_sessions(self, account_id: str) -> int:
        """Cleanup all sessions for an account"""
        count = 0
        
        # Remove from memory
        session_id = self._account_sessions.pop(account_id, None)
        if session_id:
            self._memory_sessions.pop(session_id, None)
            count += 1
        
        # Remove from database
        async for db_session in self._db_manager.get_session():
            try:
                result = await db_session.execute(
                    update(Session)
                    .where(Session.account_id == account_id)
                    .values(is_active=False)
                )
                count = result.rowcount
                await db_session.commit()
                break
            except Exception:
                await db_session.rollback()
        
        return count