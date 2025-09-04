"""
SQLite Database Manager for Trade Buddy SDK
Optimized for SQLite with async support
"""

import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Optional
from pathlib import Path

from trade_buddy.entities.models import Account, Transaction, Session


class DatabaseManager:
    """SQLite database manager with async support"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize SQLite database manager
        
        Args:
            database_url: SQLite database URL. If None, defaults to ./data/tradebuddy.db
        """
        if database_url is None:
            db_dir = Path("data")
            db_dir.mkdir(exist_ok=True)
            database_url = f"sqlite+aiosqlite:///{db_dir}/tradebuddy.db"
        
        self.database_url = database_url
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[sessionmaker] = None
        
    def _get_engine(self) -> AsyncEngine:
        """Get SQLite async engine instance"""
        if self._engine is None:
            self._engine = create_async_engine(
                self.database_url,
                echo=False,  # Set to True for SQL query debugging
                connect_args={"check_same_thread": False},
                pool_pre_ping=True,
                pool_recycle=300
            )
        return self._engine
    
    def _get_session_factory(self) -> sessionmaker:
        """Get session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self._get_engine(),
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._session_factory
    
    async def create_tables(self):
        """Create all database tables"""
        engine = self._get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    
    async def drop_tables(self):
        """Drop all database tables"""
        engine = self._get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        session_factory = self._get_session_factory()
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()
    
    async def truncate_all_tables(self):
        """Clear all data from tables"""
        async for session in self.get_session():
            try:
                from sqlalchemy import text
                
                # Delete in correct order to respect foreign key constraints
                await session.execute(text("DELETE FROM sessions"))
                await session.execute(text("DELETE FROM transactions"))
                await session.execute(text("DELETE FROM accounts"))
                
                # Reset SQLite sequences
                await session.execute(text("DELETE FROM sqlite_sequence"))
                
                await session.commit()
                break
            except Exception as e:
                await session.rollback()
                raise e
    
    async def clear_account_data(self, account_id: str):
        """Clear all data for a specific account"""
        async for session in self.get_session():
            try:
                from sqlalchemy import text
                
                # Delete in correct order
                await session.execute(text("DELETE FROM sessions WHERE account_id = :account_id"), {"account_id": account_id})
                await session.execute(text("DELETE FROM transactions WHERE account_id = :account_id"), {"account_id": account_id})
                await session.execute(text("DELETE FROM accounts WHERE account_id = :account_id"), {"account_id": account_id})
                
                await session.commit()
                break
            except Exception as e:
                await session.rollback()
                raise e
    
    async def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        async for session in self.get_session():
            try:
                from sqlalchemy import text
                await session.execute(text("DELETE FROM sessions WHERE expires_at < datetime('now') OR is_active = 0"))
                await session.commit()
                break
            except Exception as e:
                await session.rollback()
                raise e
    
    async def close(self):
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        try:
            # Use environment variable or default to SQLite
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                db_dir = Path("data")
                db_dir.mkdir(exist_ok=True)
                db_url = f"sqlite+aiosqlite:///{db_dir}/tradebuddy.db"
            
            db_manager = DatabaseManager(db_url)
        except Exception as e:
            print(f"Database manager creation warning: {e}")
            # Return a mock database manager for testing
            db_manager = None
    return db_manager


async def initialize_database():
    """Initialize database tables"""
    db = get_database_manager()
    await db.create_tables()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection"""
    db = get_database_manager()
    async for session in db.get_session():
        yield session