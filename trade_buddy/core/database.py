"""
Async database layer for Trade Buddy SDK
Supports SQLite (default) and PostgreSQL for production
"""

import os
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Optional
from pathlib import Path

from trade_buddy.entities.models import Account, Position, Order, Transaction, Ticket


class DatabaseManager:
    """Database manager with async support"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_url: Database URL. If None, defaults to SQLite
        """
        # Set default database URL for SQLite
        if database_url is None:
            db_dir = Path("data")
            db_dir.mkdir(exist_ok=True)
            database_url = f"sqlite+aiosqlite:///{db_dir}/tradebuddy.db"
        
        self.database_url = database_url
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[sessionmaker] = None
        
    def _get_engine(self) -> AsyncEngine:
        """Get async engine instance"""
        if self._engine is None:
            if "sqlite" in self.database_url:
                # SQLite configuration
                self._engine = create_async_engine(
                    self.database_url,
                    echo=False,  # Set to True for SQL query logging
                    connect_args={"check_same_thread": False}
                )
            else:
                # PostgreSQL configuration
                self._engine = create_async_engine(
                    self.database_url,
                    echo=False,
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
        """Truncate all tables (clear data but keep structure)"""
        async for session in self.get_session():
            try:
                # Delete in correct order to respect foreign key constraints
                from sqlalchemy import text
                
                await session.execute(text("DELETE FROM orders"))
                await session.execute(text("DELETE FROM transactions"))
                await session.execute(text("DELETE FROM positions"))
                await session.execute(text("DELETE FROM tickets"))
                await session.execute(text("DELETE FROM accounts"))
                
                # Reset SQLite sequences if using SQLite
                if "sqlite" in self.database_url:
                    await session.execute(text("DELETE FROM sqlite_sequence"))
                
                await session.commit()
                break  # Exit the async generator
            except Exception as e:
                await session.rollback()
                raise e
    
    async def clear_account_data(self, account_id: str):
        """Clear all data for a specific account"""
        async for session in self.get_session():
            try:
                from sqlalchemy import text
                
                # Delete in correct order to respect foreign key constraints
                await session.execute(text("DELETE FROM orders WHERE account_id = :account_id"), {"account_id": account_id})
                await session.execute(text("DELETE FROM transactions WHERE account_id = :account_id"), {"account_id": account_id})
                await session.execute(text("DELETE FROM positions WHERE account_id = :account_id"), {"account_id": account_id})
                await session.execute(text("DELETE FROM accounts WHERE account_id = :account_id"), {"account_id": account_id})
                
                await session.commit()
                break  # Exit the async generator
            except Exception as e:
                await session.rollback()
                raise e
    
    async def close(self):
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()


class DatabaseConfig:
    """Database configuration helper"""
    
    @staticmethod
    def get_sqlite_url(db_name: str = "tradebuddy.db", db_dir: str = "data") -> str:
        """Get SQLite database URL"""
        db_path = Path(db_dir)
        db_path.mkdir(exist_ok=True)
        return f"sqlite+aiosqlite:///{db_path}/{db_name}"
    
    @staticmethod
    def get_postgresql_url(
        host: str = "localhost",
        port: int = 5432,
        database: str = "tradebuddy",
        username: str = "postgres",
        password: str = "password"
    ) -> str:
        """Get PostgreSQL database URL"""
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
    
    @staticmethod
    def from_env() -> str:
        """Get database URL from environment variables"""
        db_url = os.getenv("DATABASE_URL")
        
        if db_url:
            # If using PostgreSQL, ensure we use asyncpg driver
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
            return db_url
        
        # Default to SQLite
        return DatabaseConfig.get_sqlite_url()


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        db_url = DatabaseConfig.from_env()
        db_manager = DatabaseManager(db_url)
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