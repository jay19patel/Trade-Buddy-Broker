from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from trade_buddy.entities.models import Notification


class NotificationProvider(ABC):
    """Abstract provider for sending notifications"""
    
    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """Send notification using this provider"""
        pass


class DatabaseNotificationProvider(NotificationProvider):
    """Provider for storing notifications in database"""
    
    def __init__(self, notification_repository):
        self.notification_repository = notification_repository
    
    async def send(self, notification: Notification) -> bool:
        try:
            await self.notification_repository.create(notification)
            return True
        except Exception as e:
            print(f"Error storing notification in database: {e}")
            return False


class EmailNotificationProvider(NotificationProvider):
    """Provider for sending email notifications (placeholder)"""
    
    def __init__(self, smtp_config: Optional[Dict[str, Any]] = None):
        self.smtp_config = smtp_config or {}
    
    async def send(self, notification: Notification) -> bool:
        try:
            print(f"EMAIL NOTIFICATION: {notification.title} - {notification.message}")
            return True
        except Exception as e:
            print(f"Error sending email notification: {e}")
            return False


