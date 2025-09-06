from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from trade_buddy.entities.models import Notification, NotificationType, NotificationStatus

class NotificationStrategy(ABC):
    """Abstract strategy for sending notifications"""
    
    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """Send notification using this strategy"""
        pass

class DatabaseNotificationStrategy(NotificationStrategy):
    """Strategy for storing notifications in database"""
    
    def __init__(self, notification_repository):
        self.notification_repository = notification_repository
    
    async def send(self, notification: Notification) -> bool:
        """Store notification in database"""
        try:
            await self.notification_repository.create(notification)
            return True
        except Exception as e:
            print(f"Error storing notification in database: {e}")
            return False

class EmailNotificationStrategy(NotificationStrategy):
    """Strategy for sending email notifications (placeholder for future implementation)"""
    
    def __init__(self, smtp_config: Optional[Dict[str, Any]] = None):
        self.smtp_config = smtp_config or {}
    
    async def send(self, notification: Notification) -> bool:
        """Send notification via email (placeholder)"""
        try:
            # TODO: Implement actual email sending logic
            # For now, just log the notification
            print(f"EMAIL NOTIFICATION: {notification.title} - {notification.message}")
            
            # In future, implement:
            # - SMTP connection
            # - Email template rendering
            # - Attachment support
            # - Retry logic
            
            return True
        except Exception as e:
            print(f"Error sending email notification: {e}")
            return False

class SMSNotificationStrategy(NotificationStrategy):
    """Strategy for sending SMS notifications (placeholder for future implementation)"""
    
    def __init__(self, sms_config: Optional[Dict[str, Any]] = None):
        self.sms_config = sms_config or {}
    
    async def send(self, notification: Notification) -> bool:
        """Send notification via SMS (placeholder)"""
        try:
            # TODO: Implement actual SMS sending logic
            # For now, just log the notification
            print(f"SMS NOTIFICATION: {notification.title} - {notification.message}")
            
            # In future, implement:
            # - SMS gateway integration
            # - Message formatting
            # - Delivery status tracking
            
            return True
        except Exception as e:
            print(f"Error sending SMS notification: {e}")
            return False

class PushNotificationStrategy(NotificationStrategy):
    """Strategy for sending push notifications (placeholder for future implementation)"""
    
    def __init__(self, push_config: Optional[Dict[str, Any]] = None):
        self.push_config = push_config or {}
    
    async def send(self, notification: Notification) -> bool:
        """Send notification via push (placeholder)"""
        try:
            # TODO: Implement actual push notification logic
            # For now, just log the notification
            print(f"PUSH NOTIFICATION: {notification.title} - {notification.message}")
            
            # In future, implement:
            # - FCM/APNS integration
            # - Device token management
            # - Notification scheduling
            
            return True
        except Exception as e:
            print(f"Error sending push notification: {e}")
            return False

class NotificationContext:
    """Context class for notification strategy pattern"""
    
    def __init__(self, strategy: NotificationStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: NotificationStrategy) -> None:
        """Change the notification strategy"""
        self._strategy = strategy
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification using current strategy"""
        return await self._strategy.send(notification)

class MultiChannelNotificationStrategy(NotificationStrategy):
    """Strategy for sending notifications through multiple channels"""
    
    def __init__(self, strategies: list[NotificationStrategy]):
        self.strategies = strategies
    
    async def send(self, notification: Notification) -> bool:
        """Send notification through all strategies"""
        results = []
        for strategy in self.strategies:
            try:
                result = await strategy.send(notification)
                results.append(result)
            except Exception as e:
                print(f"Error in strategy {strategy.__class__.__name__}: {e}")
                results.append(False)
        
        # Return True if at least one strategy succeeded
        return any(results)

class NotificationStrategyFactory:
    """Factory for creating notification strategies"""
    
    @staticmethod
    def create_database_strategy(notification_repository) -> DatabaseNotificationStrategy:
        """Create database notification strategy"""
        return DatabaseNotificationStrategy(notification_repository)
    
    @staticmethod
    def create_email_strategy(smtp_config: Optional[Dict[str, Any]] = None) -> EmailNotificationStrategy:
        """Create email notification strategy"""
        return EmailNotificationStrategy(smtp_config)
    
    @staticmethod
    def create_sms_strategy(sms_config: Optional[Dict[str, Any]] = None) -> SMSNotificationStrategy:
        """Create SMS notification strategy"""
        return SMSNotificationStrategy(sms_config)
    
    @staticmethod
    def create_push_strategy(push_config: Optional[Dict[str, Any]] = None) -> PushNotificationStrategy:
        """Create push notification strategy"""
        return PushNotificationStrategy(push_config)
    
    @staticmethod
    def create_multi_channel_strategy(notification_repository, 
                                    enable_email: bool = False,
                                    enable_sms: bool = False,
                                    enable_push: bool = False,
                                    email_config: Optional[Dict[str, Any]] = None,
                                    sms_config: Optional[Dict[str, Any]] = None,
                                    push_config: Optional[Dict[str, Any]] = None) -> MultiChannelNotificationStrategy:
        """Create multi-channel notification strategy"""
        strategies = [DatabaseNotificationStrategy(notification_repository)]
        
        if enable_email:
            strategies.append(EmailNotificationStrategy(email_config))
        
        if enable_sms:
            strategies.append(SMSNotificationStrategy(sms_config))
        
        if enable_push:
            strategies.append(PushNotificationStrategy(push_config))
        
        return MultiChannelNotificationStrategy(strategies)
