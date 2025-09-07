from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from trade_buddy.entities.models import Notification, NotificationType, NotificationStatus
from trade_buddy.repositories.notification_repository import NotificationRepository
from trade_buddy.patterns.observer import Subject, NotificationObserver, ErrorObserver
from trade_buddy.core.response import TBResponse

class NotificationService(Subject):
    """Service for managing notifications in a simple, direct way"""
    
    def __init__(self):
        super().__init__()
        self.notification_repository = NotificationRepository()
        # Channel enable flags (database and push enabled by default)
        self._database_enabled: bool = True
        self._push_enabled: bool = True
        self._email_enabled: bool = False
        self._sms_enabled: bool = False

        # Optional channel configs
        self._email_config: Optional[Dict[str, Any]] = None
        self._sms_config: Optional[Dict[str, Any]] = None
        self._push_config: Optional[Dict[str, Any]] = None  # placeholder for future
        
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
            
            # Store in database if enabled
            if self._database_enabled:
                await self.notification_repository.create(notification)

            # Try optional channel deliveries (best-effort)
            await self._deliver_channels(title=title, message=message, data=data or {})
            if self._database_enabled:
                await self.notification_repository.mark_sent(notification.notification_id)
            return TBResponse(
                message="Notification created successfully",
                data={"notification": notification}
            )
                
        except Exception as e:
            try:
                if 'notification' in locals():
                    if self._database_enabled:
                        await self.notification_repository.mark_failed(notification.notification_id, str(e))
            except:
                pass
            return TBResponse(
                message=f"Error creating notification: {str(e)}",
                data=None
            )

    # ---------------------------
    # Channel configuration APIs
    # ---------------------------
    def set_email_config(self, config: Dict[str, Any]) -> None:
        """Configure SMTP for email notifications. Keys: smtp_host, smtp_port, username, password, from_email, to_email"""
        self._email_config = config or {}
        # Enabling email channel when config provided
        self._email_enabled = True if config else self._email_enabled

    def set_sms_config(self, config: Dict[str, Any]) -> None:
        """Configure SMS webhook. Keys: webhook_url, api_key, to_phone, from_id (optional)"""
        self._sms_config = config or {}
        # Enabling sms channel when config provided
        self._sms_enabled = True if config else self._sms_enabled

    def set_push_config(self, config: Dict[str, Any]) -> None:
        """Configure push provider (placeholder)"""
        self._push_config = config or {}
    # Subscription controls
    def subscribe_channels(self, channels: List[str]) -> None:
        channels = [c.lower() for c in channels]
        if "database" in channels:
            self._database_enabled = True
        if "push" in channels:
            self._push_enabled = True
        if "email" in channels:
            self._email_enabled = True
        if "sms" in channels:
            self._sms_enabled = True

    def unsubscribe_channels(self, channels: List[str]) -> None:
        channels = [c.lower() for c in channels]
        if "database" in channels:
            self._database_enabled = False
        if "push" in channels:
            self._push_enabled = False
        if "email" in channels:
            self._email_enabled = False
        if "sms" in channels:
            self._sms_enabled = False

    # ---------------------------
    # Internal helpers
    # ---------------------------
    async def _deliver_channels(self, title: str, message: str, data: Dict[str, Any]) -> None:
        tasks = []
        # Print-based push is enabled by flag, no config required
        if self._push_enabled:
            tasks.append(self._send_push(title, message, data))
        if self._email_enabled:
            tasks.append(self._send_email(title, message, data))
        if self._sms_enabled:
            tasks.append(self._send_sms(title, message, data))
        if tasks:
            # Run best-effort; don't raise if individual fails
            import asyncio
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Optionally log failures
            for r in results:
                if isinstance(r, Exception):
                    print(f"Channel delivery error: {r}")

    async def _send_push(self, title: str, message: str, data: Dict[str, Any]) -> None:
        # Placeholder push: simple print
        print(f"PUSH: {title} - {message}")

    async def _send_email(self, subject: str, body: str, data: Dict[str, Any]) -> None:
        import asyncio
        cfg = self._email_config or {}
        host = cfg.get("smtp_host")
        port = cfg.get("smtp_port", 587)
        username = cfg.get("username")
        password = cfg.get("password")
        from_email = cfg.get("from_email")
        to_email = cfg.get("to_email")
        if not all([host, port, from_email, to_email]):
            return
        content = body
        # Include simple key details if present
        if data:
            try:
                import json as _json
                content += "\n\n" + _json.dumps(data, ensure_ascii=False)
            except:
                pass

        def _send():
            import smtplib
            from email.message import EmailMessage
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email
            msg.set_content(content)
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        await asyncio.to_thread(_send)

    async def _send_sms(self, title: str, message: str, data: Dict[str, Any]) -> None:
        import asyncio
        cfg = self._sms_config or {}
        url = cfg.get("webhook_url")
        api_key = cfg.get("api_key")
        to_phone = cfg.get("to_phone")
        if not all([url, to_phone]):
            return
        payload = {
            "to": to_phone,
            "text": f"{title}: {message}",
            "meta": data
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        def _post():
            import requests
            requests.post(url, json=payload, headers=headers, timeout=10)
        await asyncio.to_thread(_post)

    # Removed telegram-specific push for now; replaced by simple print push
    
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
    
    # No strategy switching or background processing required anymore
