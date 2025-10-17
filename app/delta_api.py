from delta_rest_client import DeltaRestClient
from delta_rest_client.delta_rest_client import OrderType as DeltaOrderType
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime
from functools import wraps
import os


# ============ LOGGING SETUP ============
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"delta_api_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============ CUSTOM EXCEPTIONS ============
class DeltaAPIError(Exception):
    """Base exception for Delta API errors"""
    pass


class OrderPlacementError(DeltaAPIError):
    """Raised when order placement fails"""
    pass


class BalanceError(DeltaAPIError):
    """Raised when balance fetch fails"""
    pass


class PositionError(DeltaAPIError):
    """Raised when position operations fail"""
    pass


# ============ DECORATORS ============
def handle_api_errors(func):
    """Decorator for consistent error handling across API methods"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise DeltaAPIError(f"{func.__name__} failed: {str(e)}") from e
    return wrapper


# ============ DELTA API WRAPPER CLASS ============
class DeltaAPI:
    """
    Optimized Delta Exchange REST API Wrapper with comprehensive error handling
    """

    def __init__(self, base_url: str, api_key: str, api_secret: str,client_id: int):
        """Initialize Delta API client with validation"""
        if not all([base_url, api_key, api_secret]):
            raise ValueError("base_url, api_key, and api_secret are required")

        try:
            self.client = DeltaRestClient(
                base_url=base_url,
                api_key=api_key,
                api_secret=api_secret
            )
            self.client_id = client_id
            logger.info("✅ DeltaAPI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DeltaAPI: {str(e)}")
            raise DeltaAPIError(f"Initialization failed: {str(e)}") from e

    # ---------- Market Data ----------
    @handle_api_errors
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch ticker data for a specific symbol"""
        if not symbol:
            raise ValueError("Symbol is required")

        logger.info(f"📞 get_ticker() called with params: symbol={symbol}")
        response = self.client.get_ticker(symbol)

        if not response:
            raise DeltaAPIError(f"No ticker data received for {symbol}")

        logger.info(f"📈 get_ticker() Response: {response}")
        return response

    @handle_api_errors
    def get_all_open_positions(self) -> List[Dict[str, Any]]:
        """Fetch all open margined positions with essential fields only"""
        logger.info(f"📞 get_all_open_positions() called")
        response = self.client.request(method="GET", path="/v2/positions/margined", auth=True)
        data = response.json()

        if not data or "result" not in data:
            logger.warning("No positions data received")
            return []

        positions = data.get("result", [])

        # Return only essential fields
        cleaned = [
            {
                "symbol": pos.get("product_symbol"),
                "size": pos.get("size"),
                "entry_price": pos.get("entry_price"),
                "mark_price": pos.get("mark_price"),
                "liquidation_price": pos.get("liquidation_price"),
                "leverage": pos.get("product", {}).get("default_leverage", "N/A"),
                "margin": pos.get("margin"),
                "margin_mode": pos.get("margin_mode"),
                "unrealized_pnl": pos.get("unrealized_pnl"),
                "realized_pnl": pos.get("realized_pnl"),
                "created_at": pos.get("created_at"),
            }
            for pos in positions
        ]

        logger.info(f"📊 get_all_open_positions() Response: {cleaned}")
        return cleaned

    @handle_api_errors
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance with proper validation"""
        logger.info(f"📞 get_balance() called")

        response = self.client.request(method="GET", path="/v2/wallet/balances", auth=True)
        data = response.json()

        if not data or "result" not in data or not data["result"]:
            raise BalanceError("No balance data received from API")

        balance = data["result"][0]

        result = {
            "available_balance_usd": balance.get("available_balance", 0),
            "available_balance_inr": balance.get("available_balance_inr", 0),
        }

        logger.info(f"💰 get_balance() Response: {result}")
        return result

    # ---------- Order Management ----------
    @handle_api_errors
    def get_all_open_orders(self) -> List[Dict[str, Any]]:
        """Fetch all live orders with essential fields only"""
        logger.info(f"📞 get_all_open_orders() called")
        response = self.client.get_live_orders()
        orders = response if isinstance(response, list) else []

        # Return only essential fields
        cleaned_orders = [
            {
                "id": order.get("id"),
                "product_id": order.get("product_id"),
                "product_symbol": order.get("product_symbol"),
                "side": order.get("side"),
                "size": order.get("size"),
                "unfilled_size": order.get("unfilled_size"),
                "order_type": order.get("order_type"),
                "limit_price": order.get("limit_price"),
                "stop_price": order.get("stop_price"),
                "stop_order_type": order.get("stop_order_type"),
                "state": order.get("state"),
                "reduce_only": order.get("reduce_only"),
                "bracket_order": order.get("bracket_order"),
                "created_at": order.get("created_at"),
            }
            for order in orders
        ]

        logger.info(f"📋 get_all_open_orders() Response: {cleaned_orders}")
        return cleaned_orders

    @handle_api_errors
    def cancel_order(self, product_id: int, order_id: int) -> Dict[str, Any]:
        """Cancel a specific order with validation"""
        if not product_id or not order_id:
            raise ValueError("product_id and order_id are required")

        logger.info(f"📞 cancel_order() called with params: product_id={product_id}, order_id={order_id}")
        response = self.client.cancel_order(product_id, order_id)
        logger.info(f"❌ cancel_order() Response: {response}")
        return response

    @handle_api_errors
    def cancel_all_orders(self, product_id: Optional[int] = None) -> Dict[str, Any]:
        """Cancel all orders with detailed reporting"""
        logger.info(f"📞 cancel_all_orders() called with params: product_id={product_id}")
        live_orders = self.get_all_open_orders()

        # Filter by product_id if specified
        if product_id:
            live_orders = [o for o in live_orders if o.get("product_id") == product_id]
            logger.info(f"Filtered to {len(live_orders)} orders for product {product_id}")

        if not live_orders:
            logger.info("No orders to cancel")
            result = {
                'success': True,
                'message': 'No orders to cancel',
                'cancelled_count': 0,
                'cancelled_orders': [],
                'failed_orders': []
            }
            logger.info(f"🚫 cancel_all_orders() Response: {result}")
            return result

        cancelled_orders, failed_orders = [], []

        for order in live_orders:
            pid = order.get('product_id')
            oid = order.get('id')

            if not pid or not oid:
                failed_orders.append({'order': order, 'error': 'Missing product_id or id'})
                continue

            try:
                self.cancel_order(pid, oid)
                cancelled_orders.append(oid)
            except Exception as e:
                logger.warning(f"Failed to cancel order {oid}: {str(e)}")
                failed_orders.append({'order_id': oid, 'product_id': pid, 'error': str(e)})

        result = {
            'success': len(failed_orders) == 0,
            'cancelled_count': len(cancelled_orders),
            'cancelled_orders': cancelled_orders,
            'failed_count': len(failed_orders),
            'failed_orders': failed_orders
        }

        logger.info(f"🗑️ cancel_all_orders() Response: {result}")
        return result

    # ---------- Entry Order Management ----------
    @handle_api_errors
    def create_entry(
        self,
        product_id: int,
        size: int,
        side: str,
        entry_price: float,
        leverage: int
    ) -> Dict[str, Any]:
        """Create entry order with comprehensive validation and error handling"""
        logger.info(f"📞 create_entry() called with params: product_id={product_id}, size={size}, side={side}, entry_price={entry_price}, leverage={leverage}")

        # Input validation
        if not all([product_id, size, side, entry_price, leverage]):
            raise ValueError("All parameters (product_id, size, side, entry_price, leverage) are required")

        if side.upper() not in ["BUY", "SELL"]:
            raise ValueError(f"Invalid side '{side}'. Must be 'BUY' or 'SELL'")

        if size <= 0:
            raise ValueError(f"Size must be positive, got {size}")

        if entry_price <= 0:
            raise ValueError(f"Entry price must be positive, got {entry_price}")

        if leverage <= 0:
            raise ValueError(f"Leverage must be positive, got {leverage}")

        try:
            # Set leverage first
            self.client.set_leverage(product_id, str(leverage))
            logger.info(f"✅ Leverage set to {leverage}x")
        except Exception as e:
            raise OrderPlacementError(f"Failed to set leverage: {str(e)}") from e

        try:
            # Place entry order
            entry_order = self.client.place_order(
                product_id=product_id,
                size=size,
                side=side.lower(),
                order_type=DeltaOrderType.LIMIT,
                limit_price=str(entry_price),
            )

            if not entry_order or "id" not in entry_order:
                raise OrderPlacementError("Order placed but no order ID received")

            entry_id = entry_order["id"]

            # Prepare structured return data
            result_data = {
                "success": True,
                "entry_order": {
                    "id": entry_order.get("id"),
                    "product_id": entry_order.get("product_id"),
                    "product_symbol": entry_order.get("product_symbol"),
                    "limit_price": entry_order.get("limit_price"),
                    "size": entry_order.get("size"),
                    "side": entry_order.get("side"),
                    "order_type": entry_order.get("order_type"),
                    "state": entry_order.get("state"),
                    "time_in_force": entry_order.get("time_in_force"),
                    "created_at": entry_order.get("created_at"),
                    "leverage": leverage,
                }
            }

            logger.info(f"📝 create_entry() Response: {result_data}")
            return result_data
        except Exception as e:
            raise OrderPlacementError(f"Failed to create entry order: {str(e)}") from e

    # ---------- Stoploss + Target Management ----------
    @handle_api_errors
    def create_stoploss_target(
        self,
        product_id: int,
        symbol: str,
        stoploss_price: float,
        target_price: float,
    ) -> Dict[str, Any]:
        """Create bracket order (stoploss + target) with validation"""
        logger.info(f"📞 create_stoploss_target() called with params: product_id={product_id}, symbol={symbol}, stoploss_price={stoploss_price}, target_price={target_price}")

        # Input validation
        if not all([product_id, symbol, stoploss_price, target_price]):
            raise ValueError("All parameters (product_id, symbol, stoploss_price, target_price) are required")

        if stoploss_price <= 0:
            raise ValueError(f"Stoploss price must be positive, got {stoploss_price}")

        if target_price <= 0:
            raise ValueError(f"Target price must be positive, got {target_price}")

        payload = {
            "product_id": product_id,
            "product_symbol": symbol,
            "stop_loss_order": {
                "order_type": "market_order",
                "stop_price": str(stoploss_price)
            },
            "take_profit_order": {
                "order_type": "market_order",
                "stop_price": str(target_price)
            },
            "bracket_stop_trigger_method": "last_traded_price"
        }

        try:
            response = self.client.request(
                method="POST",
                path="/v2/orders/bracket",
                payload=payload,
                auth=True
            )

            result = response.json()

            if not result or "result" not in result:
                raise OrderPlacementError("Bracket order placed but no confirmation received")

            # Extract stop loss and take profit data
            bracket_result = result.get("result", {})
            stop_loss_order = bracket_result.get("stop_loss_order", {})
            take_profit_order = bracket_result.get("take_profit_order", {})

            # Prepare structured return data
            return_data = {
                "success": result.get("success", True),
                "stop_loss_order": {
                    "id": stop_loss_order.get("id"),
                    "product_id": stop_loss_order.get("product_id"),
                    "product_symbol": stop_loss_order.get("product_symbol"),
                    "stop_price": stop_loss_order.get("stop_price"),
                    "size": stop_loss_order.get("size"),
                    "side": stop_loss_order.get("side"),
                    "order_type": stop_loss_order.get("order_type"),
                    "state": stop_loss_order.get("state"),
                    "stop_order_type": stop_loss_order.get("stop_order_type"),
                    "created_at": stop_loss_order.get("created_at"),
                },
                "take_profit_order": {
                    "id": take_profit_order.get("id"),
                    "product_id": take_profit_order.get("product_id"),
                    "product_symbol": take_profit_order.get("product_symbol"),
                    "stop_price": take_profit_order.get("stop_price"),
                    "size": take_profit_order.get("size"),
                    "side": take_profit_order.get("side"),
                    "order_type": take_profit_order.get("order_type"),
                    "state": take_profit_order.get("state"),
                    "stop_order_type": take_profit_order.get("stop_order_type"),
                    "created_at": take_profit_order.get("created_at"),
                }
            }

            logger.info(f"🎯 create_stoploss_target() Response: {return_data}")
            return return_data

        except Exception as e:
            raise OrderPlacementError(f"Failed to create bracket order: {str(e)}") from e

    # ---------- Emergency Exit ----------
    def emergency_exit(self) -> Dict[str, Any]:
        """
        Emergency exit: Cancel all orders and close all positions

        Note: This method does NOT use @handle_api_errors decorator to provide
        maximum detail about partial failures during emergency situations.
        """
        user_id = self.client_id
        logger.warning("🚨 EMERGENCY EXIT INITIATED")
        logger.info(f"📞 emergency_exit() called")

        result = {
            "success": False,
            "orders_cancelled": 0,
            "positions_closed": False,
            "errors": []
        }

        # Step 1: Cancel all orders
        try:
            cancel_result = self.cancel_all_orders()
            result["orders_cancelled"] = cancel_result.get("cancelled_count", 0)

            if cancel_result.get("failed_orders"):
                result["errors"].append(f"{len(cancel_result['failed_orders'])} orders failed to cancel")

            logger.info(f"✅ Cancelled {result['orders_cancelled']} orders")
        except Exception as e:
            error_msg = f"Failed to cancel orders: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        # Step 2: Close all positions
        try:
            if not user_id:
                raise ValueError("user_id is required for closing positions")

            payload = {
                "close_all_portfolio": True,
                "close_all_isolated": True,
                "user_id": user_id
            }

            close_response = self.client.request(
                method="POST",
                path="/v2/positions/close_all",
                payload=payload,
                auth=True
            )

            result["positions_closed"] = True
            logger.info("✅ All positions closed")

        except Exception as e:
            error_msg = f"Failed to close positions: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        # Determine overall success
        result["success"] = result["positions_closed"] and len(result["errors"]) == 0

        if result["success"]:
            logger.warning("✅ EMERGENCY EXIT COMPLETED SUCCESSFULLY")
        else:
            logger.critical(f"⚠️ EMERGENCY EXIT COMPLETED WITH ERRORS: {result['errors']}")

        logger.info(f"🚨 emergency_exit() Response: {result}")
        return result


