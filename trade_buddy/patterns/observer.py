from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import traceback
import inspect

class Observer(ABC):
    """Abstract observer interface"""
    
    @abstractmethod
    async def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Update method called when an event occurs"""
        pass

class Subject(ABC):
    """Abstract subject interface for observer pattern"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    async def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers"""
        for observer in self._observers:
            try:
                await observer.update(event_type, data)
            except Exception as e:
                print(f"Error notifying observer {observer.__class__.__name__}: {e}")

class NotificationObserver(Observer):
    """Observer for handling notifications"""
    
    def __init__(self, notification_service):
        self.notification_service = notification_service
    
    async def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle notification events"""
        try:
            if event_type == "transaction_created":
                await self._handle_transaction_created(data)
            elif event_type == "position_opened":
                await self._handle_position_opened(data)
            elif event_type == "position_updated":
                await self._handle_position_updated(data)
            elif event_type == "position_closed":
                await self._handle_position_closed(data)
            elif event_type == "position_pyramided":
                await self._handle_position_pyramided(data)
            elif event_type == "position_trailed":
                await self._handle_position_trailed(data)
            elif event_type == "leverage_updated":
                await self._handle_leverage_updated(data)
            elif event_type == "error_occurred":
                await self._handle_error_occurred(data)
        except Exception as e:
            print(f"Error in NotificationObserver: {e}")
    
    async def _handle_transaction_created(self, data: Dict[str, Any]) -> None:
        """Handle transaction created event"""
        transaction = data.get("transaction")
        account_id = data.get("account_id")
        
        if transaction and account_id:
            # Handle both dict and object types
            if isinstance(transaction, dict):
                transaction_type = transaction.get("transaction_type")
                transaction_amount = transaction.get("transaction_amount")
                transaction_id = transaction.get("transaction_id")
            else:
                transaction_type = transaction.transaction_type
                transaction_amount = transaction.transaction_amount
                transaction_id = transaction.transaction_id
            
            await self.notification_service.create_notification(
                account_id=account_id,
                notification_type="TRANSACTION",
                title="Transaction Completed",
                message=f"{transaction_type} of ₹{transaction_amount} completed successfully",
                data={
                    "transaction_id": transaction_id,
                    "amount": transaction_amount,
                    "type": str(transaction_type)
                }
            )
    
    async def _handle_position_opened(self, data: Dict[str, Any]) -> None:
        """Handle position opened event"""
        position = data.get("position")
        account_id = data.get("account_id")
        
        if position and account_id:
            await self.notification_service.create_notification(
                account_id=account_id,
                notification_type="POSITION",
                title="Position Opened",
                message=f"Opened {position.side} position in {position.symbol_id} with {position.quantity} shares at ₹{position.avg_price}",
                data={
                    "position_id": position.position_id,
                    "symbol": position.symbol_id,
                    "side": position.side,
                    "quantity": position.quantity,
                    "price": position.avg_price,
                    "leverage": position.leverage
                }
            )
    
    async def _handle_position_updated(self, data: Dict[str, Any]) -> None:
        """Handle position updated event"""
        position = data.get("position")
        account_id = data.get("account_id")
        changes = data.get("changes", {})
        
        if position and account_id:
            change_messages = []
            if "stoploss" in changes:
                change_messages.append(f"Stop Loss: ₹{changes['stoploss']}")
            if "target" in changes:
                change_messages.append(f"Target: ₹{changes['target']}")
            
            message = f"Position {position.position_id} updated"
            if change_messages:
                message += f" - {', '.join(change_messages)}"
            
            await self.notification_service.create_notification(
                account_id=account_id,
                notification_type="POSITION",
                title="Position Updated",
                message=message,
                data={
                    "position_id": position.position_id,
                    "changes": changes
                }
            )
    
    async def _handle_position_closed(self, data: Dict[str, Any]) -> None:
        """Handle position closed event"""
        position = data.get("position")
        account_id = data.get("account_id")
        
        if position and account_id:
            pnl_text = f"P&L: ₹{position.pnl}" if position.pnl else "P&L: Calculating..."
            await self.notification_service.create_notification(
                account_id=account_id,
                notification_type="POSITION",
                title="Position Closed",
                message=f"Closed {position.side} position in {position.symbol_id} at ₹{position.exit_price} - {pnl_text}",
                data={
                    "position_id": position.position_id,
                    "symbol": position.symbol_id,
                    "exit_price": position.exit_price,
                    "pnl": position.pnl,
                    "pnl_percentage": position.pnl_percentage
                }
            )
    
    async def _handle_position_pyramided(self, data: Dict[str, Any]) -> None:
        """Handle position pyramided event"""
        position = data.get("position")
        account_id = data.get("account_id")
        additional_quantity = data.get("additional_quantity")
        new_price = data.get("new_price")
        
        if position and account_id:
            await self.notification_service.create_notification(
                account_id=account_id,
                notification_type="POSITION",
                title="Position Pyramided",
                message=f"Added {additional_quantity} shares to position at ₹{new_price}. Total quantity: {position.total_quantity}",
                data={
                    "position_id": position.position_id,
                    "additional_quantity": additional_quantity,
                    "new_price": new_price,
                    "total_quantity": position.total_quantity
                }
            )
    
    async def _handle_position_trailed(self, data: Dict[str, Any]) -> None:
        """Handle position trailed event"""
        position = data.get("position")
        account_id = data.get("account_id")
        close_quantity = data.get("close_quantity")
        exit_price = data.get("exit_price")
        
        if position and account_id:
            await self.notification_service.create_notification(
                account_id=account_id,
                notification_type="POSITION",
                title="Position Trailed",
                message=f"Partially closed {close_quantity} shares at ₹{exit_price}. Remaining: {position.remaining_quantity}",
                data={
                    "position_id": position.position_id,
                    "close_quantity": close_quantity,
                    "exit_price": exit_price,
                    "remaining_quantity": position.remaining_quantity
                }
            )
    
    async def _handle_leverage_updated(self, data: Dict[str, Any]) -> None:
        """Handle leverage updated event"""
        account_id = data.get("account_id")
        old_leverage = data.get("old_leverage")
        new_leverage = data.get("new_leverage")
        
        if account_id:
            await self.notification_service.create_notification(
                account_id=account_id,
                notification_type="SYSTEM",
                title="Leverage Updated",
                message=f"Default leverage changed from {old_leverage}x to {new_leverage}x",
                data={
                    "old_leverage": old_leverage,
                    "new_leverage": new_leverage
                }
            )
    
    async def _handle_error_occurred(self, data: Dict[str, Any]) -> None:
        """Handle error occurred event"""
        account_id = data.get("account_id")
        error = data.get("error")
        function_name = data.get("function_name")
        class_name = data.get("class_name")
        file_name = data.get("file_name")
        
        if account_id and error:
            error_message = str(error)
            error_class = error.__class__.__name__ if error else class_name
            
            await self.notification_service.create_notification(
                account_id=account_id,
                notification_type="ERROR",
                title="Error Occurred",
                message=f"Error in {function_name}: {error_message}",
                data={
                    "error_message": error_message,
                    "function_name": function_name,
                    "class_name": class_name,
                    "file_name": file_name
                },
                error_class=error_class,
                error_function=function_name,
                error_file=file_name
            )

class ErrorObserver(Observer):
    """Observer for handling errors and exceptions"""
    
    def __init__(self, notification_service):
        self.notification_service = notification_service
    
    async def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle error events"""
        if event_type == "error_occurred":
            await self._handle_error(data)
    
    async def _handle_error(self, data: Dict[str, Any]) -> None:
        """Handle error data"""
        try:
            account_id = data.get("account_id")
            error = data.get("error")
            function_name = data.get("function_name", "Unknown")
            class_name = data.get("class_name", "Unknown")
            
            # Get file name and line number from traceback
            file_name = "Unknown"
            line_number = 0
            try:
                tb = traceback.extract_tb(error.__traceback__)
                if tb:
                    file_name = tb[-1].filename
                    line_number = tb[-1].lineno
            except:
                pass
            
            if account_id:
                await self.notification_service.create_notification(
                    account_id=account_id,
                    notification_type="ERROR",
                    title="System Error",
                    message=f"Error in {function_name}: {str(error)}",
                    data={
                        "error_message": str(error),
                        "function_name": function_name,
                        "class_name": class_name,
                        "file_name": file_name,
                        "line_number": line_number
                    },
                    error_class=error.__class__.__name__,
                    error_function=function_name,
                    error_file=file_name,
                    error_line=line_number
                )
        except Exception as e:
            print(f"Error in ErrorObserver: {e}")

def get_caller_info() -> Dict[str, str]:
    """Get caller information for error tracking"""
    try:
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back  # Go up 2 levels to get the actual caller
        return {
            "function_name": caller_frame.f_code.co_name,
            "class_name": caller_frame.f_locals.get('self', type(None)).__class__.__name__ if 'self' in caller_frame.f_locals else "Unknown",
            "file_name": caller_frame.f_code.co_filename
        }
    except:
        return {
            "function_name": "Unknown",
            "class_name": "Unknown", 
            "file_name": "Unknown"
        }
