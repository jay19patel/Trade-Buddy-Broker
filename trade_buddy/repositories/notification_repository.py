from typing import List, Optional, Dict, Any
from sqlmodel import select, update, delete
from datetime import datetime, timezone
from trade_buddy.entities.models import Notification, NotificationType, NotificationStatus
from trade_buddy.core.database import get_database_manager
from trade_buddy.repositories.base import BaseRepository

class NotificationRepository(BaseRepository[Notification]):
    """Repository for managing notifications"""
    
    def __init__(self):
        self._notifications: Dict[str, Notification] = {}
    
    async def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        db = get_database_manager()
        async for session in db.get_session():
            session.add(notification)
            await session.commit()
            await session.refresh(notification)
            return notification
    
    async def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Notification).where(Notification.notification_id == notification_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_by_account(self, account_id: str, limit: int = 50) -> List[Notification]:
        """Get notifications for an account"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = (
                select(Notification)
                .where(Notification.account_id == account_id)
                .order_by(Notification.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_by_account_paginated(self, account_id: str, page: int = 1, page_size: int = 20) -> List[Notification]:
        """Paginated notifications for an account"""
        db = get_database_manager()
        async for session in db.get_session():
            offset_val = max(0, (page - 1) * page_size)
            stmt = (
                select(Notification)
                .where(Notification.account_id == account_id)
                .order_by(Notification.created_at.desc())
                .offset(offset_val)
                .limit(page_size)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def get_by_type(self, account_id: str, notification_type: NotificationType, limit: int = 20) -> List[Notification]:
        """Get notifications by type for an account"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = (
                select(Notification)
                .where(
                    Notification.account_id == account_id,
                    Notification.notification_type == notification_type
                )
                .order_by(Notification.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def get_pending(self, limit: int = 100) -> List[Notification]:
        """Get pending notifications"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = (
                select(Notification)
                .where(Notification.status == NotificationStatus.PENDING)
                .order_by(Notification.created_at.asc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def update(self, notification_id: str, **kwargs) -> Optional[Notification]:
        """Update notification"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = (
                update(Notification)
                .where(Notification.notification_id == notification_id)
                .values(**kwargs)
            )
            await session.execute(stmt)
            await session.commit()
            
            # Return updated notification
            stmt = select(Notification).where(Notification.notification_id == notification_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def mark_sent(self, notification_id: str) -> bool:
        """Mark notification as sent"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = (
                update(Notification)
                .where(Notification.notification_id == notification_id)
                .values(
                    status=NotificationStatus.SENT,
                    sent_at=datetime.now(timezone.utc)
                )
            )
            await session.execute(stmt)
            await session.commit()
            return True
    
    async def mark_failed(self, notification_id: str, error_message: str) -> bool:
        """Mark notification as failed"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = (
                update(Notification)
                .where(Notification.notification_id == notification_id)
                .values(
                    status=NotificationStatus.FAILED,
                    error_message=error_message
                )
            )
            await session.execute(stmt)
            await session.commit()
            return True
    
    async def delete(self, notification_id: str) -> bool:
        """Delete notification"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = delete(Notification).where(Notification.notification_id == notification_id)
            await session.execute(stmt)
            await session.commit()
            return True
    
    async def get_all(self) -> List[Notification]:
        """Get all notifications"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = select(Notification).order_by(Notification.created_at.desc())
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def clear_all(self) -> bool:
        """Clear all notifications"""
        db = get_database_manager()
        async for session in db.get_session():
            stmt = delete(Notification)
            await session.execute(stmt)
            await session.commit()
            return True
