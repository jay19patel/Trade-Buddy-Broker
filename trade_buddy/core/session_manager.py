"""
Pure Database Session Manager
- SQLite database-only storage
- No in-memory cache
- Persistent across system restarts
- Clean minimal implementation
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import select, update

from trade_buddy.entities.models import Account, Session
from trade_buddy.utils.security import SecurityManager
from trade_buddy.utils.singleton import Singleton
from trade_buddy.core.database import get_database_manager


class DatabaseSessionManager(Singleton):
    """
    Pure Database Session Manager
    
    Features:
    🗄️ SQLite database-only storage
    🔄 Persistent across restarts
    🔑 JWT token integration
    👥 Multi-user support
    🧹 Automatic cleanup
    📊 Simple & reliable
    """
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._security = SecurityManager()
            self._db_manager = get_database_manager()
            if self._db_manager is None:
                raise RuntimeError("Database manager is not initialized")
            self.token_expiry_hours = 24
            self.initialized = True
    
    async def create_session(
        self, 
        account: Account, 
        device_info: Optional[str] = None, 
        ip_address: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Create new session in database
        
        Returns:
            Tuple of (session_id, jwt_token)
        """
        # Generate session ID and JWT token
        session_id = self._security.generate_unique_id("SESSION")
        
        # Create JWT token
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
        
        # Remove existing sessions for this account
        await self._cleanup_account_sessions(account.account_id)
        
        # Create database session record
        async for db_session in self._db_manager.get_session():
            try:
                session_obj = Session(
                    session_id=session_id,
                    account_id=account.account_id,
                    jwt_token=jwt_token,
                    device_info=device_info or "Trade Buddy SDK",
                    ip_address=ip_address or "localhost",
                    expires_at=expires_at,
                    is_active=True
                )
                
                db_session.add(session_obj)
                await db_session.commit()
                break
            except Exception as e:
                await db_session.rollback()
                raise e
        
        return session_id, jwt_token
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from database"""
        async for db_session in self._db_manager.get_session():
            try:
                stmt = select(Session).where(
                    Session.session_id == session_id,
                    Session.is_active == True
                )
                result = await db_session.execute(stmt)
                session_obj = result.scalar_one_or_none()
                
                if session_obj and session_obj.expires_at > datetime.now():
                    # Update last activity
                    await db_session.execute(
                        update(Session)
                        .where(Session.session_id == session_id)
                        .values(last_activity=datetime.now())
                    )
                    await db_session.commit()
                    
                    return {
                        "session_id": session_obj.session_id,
                        "account_id": session_obj.account_id,
                        "jwt_token": session_obj.jwt_token,
                        "device_info": session_obj.device_info,
                        "ip_address": session_obj.ip_address,
                        "created_at": session_obj.created_at,
                        "last_activity": session_obj.last_activity,
                        "expires_at": session_obj.expires_at
                    }
                
                return None
                
            except Exception:
                return None
    
    async def get_account_session(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get active session for account"""
        async for db_session in self._db_manager.get_session():
            try:
                stmt = select(Session).where(
                    Session.account_id == account_id,
                    Session.is_active == True
                )
                result = await db_session.execute(stmt)
                session_obj = result.scalar_one_or_none()
                
                if session_obj:
                    return await self.get_session(session_obj.session_id)
                
                return None
            except Exception:
                return None
    
    async def validate_session(self, session_id: str) -> bool:
        """Validate session and JWT token"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
        
        # Validate JWT token
        try:
            payload = self._security.decode_token(session_data['jwt_token'])
            return payload.get("SessionId") == session_id
        except:
            await self.destroy_session(session_id)
            return False
    
    async def validate_jwt_token(self, jwt_token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return session"""
        try:
            payload = self._security.decode_token(jwt_token)
            session_id = payload.get("SessionId")
            
            if session_id:
                return await self.get_session(session_id)
            
            return None
        except:
            return None
    
    async def destroy_session(self, session_id: str) -> bool:
        """Destroy session (logout)"""
        async for db_session in self._db_manager.get_session():
            try:
                result = await db_session.execute(
                    update(Session)
                    .where(Session.session_id == session_id)
                    .values(is_active=False)
                )
                await db_session.commit()
                return result.rowcount > 0
            except Exception:
                await db_session.rollback()
                return False
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information with account details"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return None
        
        # Get account details
        from trade_buddy.repositories import AccountRepository
        account_repo = AccountRepository()
        account = await account_repo.get_by_id(session_data['account_id'])
        
        if account:
            return {
                "session_id": session_data['session_id'],
                "account_id": account.account_id,
                "email": account.email_id,
                "full_name": account.full_name,
                "balance": account.balance,
                "created_at": session_data['created_at'].isoformat(),
                "last_activity": session_data['last_activity'].isoformat(),
                "expires_at": session_data['expires_at'].isoformat(),
                "device_info": session_data['device_info'],
                "ip_address": session_data['ip_address']
            }
        
        return None
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        sessions = []
        async for db_session in self._db_manager.get_session():
            try:
                stmt = select(Session).where(
                    Session.is_active == True,
                    Session.expires_at > datetime.now()
                )
                result = await db_session.execute(stmt)
                session_objects = result.scalars().all()
                
                for session_obj in session_objects:
                    sessions.append({
                        "session_id": session_obj.session_id,
                        "account_id": session_obj.account_id,
                        "device_info": session_obj.device_info,
                        "ip_address": session_obj.ip_address,
                        "created_at": session_obj.created_at.isoformat(),
                        "last_activity": session_obj.last_activity.isoformat(),
                        "expires_at": session_obj.expires_at.isoformat()
                    })
                
                break
            except Exception:
                pass
        
        return sessions
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions (sync method)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return 0  # Cannot get count in running loop
            return len(loop.run_until_complete(self.get_active_sessions()))
        except:
            return 0
    
    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions from database"""
        async for db_session in self._db_manager.get_session():
            try:
                result = await db_session.execute(
                    update(Session)
                    .where(Session.expires_at < datetime.now())
                    .values(is_active=False)
                )
                await db_session.commit()
                return result.rowcount
            except Exception:
                await db_session.rollback()
                return 0
    
    async def clear_all_sessions(self):
        """Clear all sessions"""
        async for db_session in self._db_manager.get_session():
            try:
                await db_session.execute(
                    update(Session)
                    .values(is_active=False)
                )
                await db_session.commit()
                break
            except Exception:
                await db_session.rollback()
    
    async def _cleanup_account_sessions(self, account_id: str) -> int:
        """Cleanup all sessions for an account"""
        async for db_session in self._db_manager.get_session():
            try:
                result = await db_session.execute(
                    update(Session)
                    .where(Session.account_id == account_id)
                    .values(is_active=False)
                )
                await db_session.commit()
                return result.rowcount
            except Exception:
                await db_session.rollback()
                return 0