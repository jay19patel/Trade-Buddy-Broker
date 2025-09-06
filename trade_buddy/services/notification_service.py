from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from trade_buddy.entities.models import Notification, NotificationType, NotificationStatus
from trade_buddy.repositories.notification_repository import NotificationRepository
from trade_buddy.patterns.strategy import NotificationStrategyFactory, NotificationContext
from trade_buddy.patterns.observer import Subject, NotificationObserver, ErrorObserver
from trade_buddy.core.response import TBResponse

class NotificationService(Subject):
    """Service for managing notifications with observer pattern and strategy pattern"""
    
    def __init__(self):
        super().__init__()
        self.notification_repository = NotificationRepository()
        
        # Initialize notification strategy (database by default)
        self.notification_strategy = NotificationStrategyFactory.create_database_strategy(
            self.notification_repository
        )
        self.notification_context = NotificationContext(self.notification_strategy)
        
        # Attach observers
        self.notification_observer = NotificationObserver(self)
        self.error_observer = ErrorObserver(self)
        self.attach(self.notification_observer)
        self.attach(self.error_observer)
    
    async def create_notification(self, 
                                account_id: str,
                                notification_type: str,
                                title: str,
                                message: str,
                                data: Optional[Dict[str, Any]] = None,
                                error_class: Optional[str] = None,
                                error_function: Optional[str] = None,
                                error_file: Optional[str] = None,
                                error_line: Optional[int] = None) -> TBResponse:
        """Create a new notification"""
        try:
            # Convert data dict to JSON string if provided
            data_json = None
            if data:
                import json
                data_json = json.dumps(data)
            
            notification = Notification(
                account_id=account_id,
                notification_type=NotificationType(notification_type),
                title=title,
                message=message,
                data=data_json,
                error_class=error_class,
                error_function=error_function,
                error_file=error_file,
                error_line=error_line
            )
            
            # Send notification using current strategy
            success = await self.notification_context.send_notification(notification)
            
            if success:
                return TBResponse(
                    message="Notification created successfully",
                    data={"notification": notification}
                )
            else:
                return TBResponse(
                    message="Failed to create notification",
                    data=None
                )
                
        except Exception as e:
            return TBResponse(
                message=f"Error creating notification: {str(e)}",
                data=None
            )
    
    async def get_notifications(self, account_id: str, limit: int = 50) -> TBResponse:
        """Get notifications for an account"""
        try:
            notifications = await self.notification_repository.get_by_account(account_id, limit)
            return TBResponse(
                message="Notifications retrieved successfully",
                data={"notifications": notifications}
            )
        except Exception as e:
            return TBResponse(
                message=f"Error retrieving notifications: {str(e)}",
                data=None
            )
    
    async def get_notifications_by_type(self, account_id: str, notification_type: str, limit: int = 20) -> TBResponse:
        """Get notifications by type for an account"""
        try:
            notifications = await self.notification_repository.get_by_type(
                account_id, 
                NotificationType(notification_type), 
                limit
            )
            return TBResponse(
                message="Notifications retrieved successfully",
                data={"notifications": notifications}
            )
        except Exception as e:
            return TBResponse(
                message=f"Error retrieving notifications: {str(e)}",
                data=None
            )
    
    async def get_pending_notifications(self, limit: int = 100) -> TBResponse:
        """Get pending notifications"""
        try:
            notifications = await self.notification_repository.get_pending(limit)
            return TBResponse(
                message="Pending notifications retrieved successfully",
                data={"notifications": notifications}
            )
        except Exception as e:
            return TBResponse(
                message=f"Error retrieving pending notifications: {str(e)}",
                data=None
            )
    
    async def mark_notification_sent(self, notification_id: str) -> TBResponse:
        """Mark notification as sent"""
        try:
            success = await self.notification_repository.mark_sent(notification_id)
            if success:
                return TBResponse(
                    message="Notification marked as sent",
                    data={"notification_id": notification_id}
                )
            else:
                return TBResponse(
                    message="Failed to mark notification as sent",
                    data=None
                )
        except Exception as e:
            return TBResponse(
                message=f"Error marking notification as sent: {str(e)}",
                data=None
            )
    
    async def mark_notification_failed(self, notification_id: str, error_message: str) -> TBResponse:
        """Mark notification as failed"""
        try:
            success = await self.notification_repository.mark_failed(notification_id, error_message)
            if success:
                return TBResponse(
                    message="Notification marked as failed",
                    data={"notification_id": notification_id}
                )
            else:
                return TBResponse(
                    message="Failed to mark notification as failed",
                    data=None
                )
        except Exception as e:
            return TBResponse(
                message=f"Error marking notification as failed: {str(e)}",
                data=None
            )
    
    async def delete_notification(self, notification_id: str) -> TBResponse:
        """Delete notification"""
        try:
            success = await self.notification_repository.delete(notification_id)
            if success:
                return TBResponse(
                    message="Notification deleted successfully",
                    data={"notification_id": notification_id}
                )
            else:
                return TBResponse(
                    message="Failed to delete notification",
                    data=None
                )
        except Exception as e:
            return TBResponse(
                message=f"Error deleting notification: {str(e)}",
                data=None
            )
    
    def set_notification_strategy(self, strategy_type: str, **kwargs) -> None:
        """Change notification strategy"""
        if strategy_type == "database":
            self.notification_strategy = NotificationStrategyFactory.create_database_strategy(
                self.notification_repository
            )
        elif strategy_type == "email":
            self.notification_strategy = NotificationStrategyFactory.create_email_strategy(
                kwargs.get("email_config")
            )
        elif strategy_type == "sms":
            self.notification_strategy = NotificationStrategyFactory.create_sms_strategy(
                kwargs.get("sms_config")
            )
        elif strategy_type == "push":
            self.notification_strategy = NotificationStrategyFactory.create_push_strategy(
                kwargs.get("push_config")
            )
        elif strategy_type == "multi_channel":
            self.notification_strategy = NotificationStrategyFactory.create_multi_channel_strategy(
                self.notification_repository,
                enable_email=kwargs.get("enable_email", False),
                enable_sms=kwargs.get("enable_sms", False),
                enable_push=kwargs.get("enable_push", False),
                email_config=kwargs.get("email_config"),
                sms_config=kwargs.get("sms_config"),
                push_config=kwargs.get("push_config")
            )
        
        self.notification_context.set_strategy(self.notification_strategy)
    
    async def process_pending_notifications(self) -> TBResponse:
        """Process all pending notifications"""
        try:
            pending_notifications = await self.notification_repository.get_pending()
            processed_count = 0
            failed_count = 0
            
            for notification in pending_notifications:
                try:
                    success = await self.notification_context.send_notification(notification)
                    if success:
                        await self.notification_repository.mark_sent(notification.notification_id)
                        processed_count += 1
                    else:
                        await self.notification_repository.mark_failed(
                            notification.notification_id, 
                            "Strategy failed to send"
                        )
                        failed_count += 1
                except Exception as e:
                    await self.notification_repository.mark_failed(
                        notification.notification_id, 
                        str(e)
                    )
                    failed_count += 1
            
            return TBResponse(
                message=f"Processed {processed_count} notifications, {failed_count} failed",
                data={
                    "processed": processed_count,
                    "failed": failed_count,
                    "total": len(pending_notifications)
                }
            )
        except Exception as e:
            return TBResponse(
                message=f"Error processing pending notifications: {str(e)}",
                data=None
            )
