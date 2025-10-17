from delta_rest_client import DeltaRestClient
from delta_rest_client.delta_rest_client import OrderType as DeltaOrderType
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import os


# ============ LOGGING SETUP ============
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

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


# ============ DELTA API WRAPPER CLASS ============
class DeltaAPI:
    """
    Simplified Delta Exchange REST API Wrapper
    """

    def __init__(self, base_url: str, api_key: str, api_secret: str):
        self.client = DeltaRestClient(
            base_url=base_url,
            api_key=api_key,
            api_secret=api_secret
        )
        logger.info("✅ DeltaAPI initialized successfully")

    # ---------- Market Data ----------
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        try:
            logger.info(f"Fetching ticker for symbol: {symbol}")
            response = self.client.get_ticker(symbol)
            return response
        except Exception as e:
            logger.error(f"Error fetching ticker: {str(e)}")
            raise

    def get_all_open_positions(self) -> Dict[str, Any]:
        try:
            logger.info(f"Fetching all open positions")
            data = self.client.request(method="GET", path="/v2/positions/margined",auth=True)
            data = data.json()
            cleaned = []
            for item in data.get("result", []):
                cleaned.append({
                    "symbol": item.get("product_symbol"),
                    "entry_price": item.get("entry_price"),
                    "mark_price": item.get("mark_price"),
                    "liquidation_price": item.get("liquidation_price"),
                    "margin": item.get("margin"),
                    "leverage": item.get("product", {}).get("default_leverage", "N/A"),
                    "unrealized_pnl": item.get("unrealized_pnl"),
                    "realized_pnl": item.get("realized_pnl"),
                    "size": item.get("size"),
                    "margin_mode": item.get("margin_mode"),
                    "commission": item.get("commission"),
                    "created_at": item.get("created_at"),
                })
            return cleaned

        except Exception as e:
            logger.error(f"Error fetching position: {str(e)}")
            raise

    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance for a specific asset.
        Default asset_id=1 is usually USDT/USD.
        """
        try:
            logger.info(f"Fetching balance")
            response = self.client.request(method="GET", path="/v2/wallet/balances",auth=True)
            response = response.json().get("result", [])[0]

            logger.info(f"✅ Balance fetched successfully")
            return {
                "available_balance_usd":response.get("available_balance"),
                "available_balance_inr":response.get("available_balance_inr"),
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            raise

    # ---------- Order Management ----------
    def get_live_orders(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.get_live_orders()
            logger.info(f"Fetched {len(response)} live orders")
            return response
        except Exception as e:
            logger.error(f"Error fetching live orders: {str(e)}")
            raise

    def cancel_order(self, product_id: int, order_id: int) -> Dict[str, Any]:
        try:
            logger.info(f"Cancelling order {order_id} for product {product_id}")
            response = self.client.cancel_order(product_id, order_id)
            logger.info(f"Order {order_id} cancelled successfully")
            return response
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {str(e)}")
            raise

    def cancel_all_orders(self, product_id: Optional[int] = None) -> Dict[str, Any]:
        try:
            live_orders = self.get_live_orders()
            if product_id:
                live_orders = [o for o in live_orders if o["product_id"] == product_id]

            if not live_orders:
                return {'success': True, 'message': 'No orders to cancel', 'cancelled_count': 0}

            cancelled_orders, failed_orders = [], []
            for order in live_orders:
                try:
                    pid = order['product_id']
                    oid = order['id']
                    self.cancel_order(pid, oid)
                    cancelled_orders.append(oid)
                except Exception as e:
                    failed_orders.append({'order_id': oid, 'error': str(e)})

            logger.info(f"Cancelled {len(cancelled_orders)} orders, failed {len(failed_orders)}")
            return {
                'success': True,
                'cancelled_count': len(cancelled_orders),
                'cancelled_orders': cancelled_orders,
                'failed_orders': failed_orders
            }
        except Exception as e:
            logger.error(f"Error cancelling all orders: {str(e)}")
            raise

    # ---------- Entry Only ----------
    def create_entry(
        self,
        product_id: int,
        size: int,
        side: str,
        entry_price: float,
        leverage: int
    ) -> Dict[str, Any]:
        """
        Create only the entry order (LIMIT) and set leverage.
        Returns the placed entry order details and id.
        """
        try:
            logger.info(f"Creating entry order for {product_id}, Side: {side}, Size: {size}")
            logger.info(f"Entry: {entry_price}, Leverage: {leverage}")

            # Set leverage for upcoming orders
            self.client.set_leverage(product_id, str(leverage))

            entry_order = self.client.place_order(
                product_id=product_id,
                size=size,
                side=side.lower(),
                order_type=DeltaOrderType.LIMIT,
                limit_price=str(entry_price),
            )

            entry_id = entry_order.get("id")
            logger.info(f"✅ Entry Order Created: {entry_id}")

            return {
                "success": True,
                "entry_order_id": entry_id,
                "response": entry_order,
            }
        except Exception as e:
            logger.error(f"❌ Error creating entry order: {str(e)}")
            raise

    # ---------- Stoploss + Target ----------
    def create_stoploss_target(
        self,
        product_id: int,
        symbol :str,
        stoploss_price: float,
        target_price: float,
    ) -> Dict[str, Any]:
        """
        Create stoploss and target as LIMIT orders on the opposite side.

        If any leg (stop/target) fails to place, cancel the successfully created
        leg(s). If an entry_order_id is provided, also attempt to cancel the entry.
        """
        try:

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
                
            
            response = self.client.request(method="POST", path="/v2/orders/bracket", payload=payload, auth=True)
            logger.info(f"✅ Stoploss/Target created successfully : {response.json()}")
            return response.json()

        except Exception as e:
            logger.error(f"❌ Error creating stoploss/target: {str(e)}")
            raise

    # ---------- Emergency Exit ----------
    def emergency_exit(self) -> Dict[str, Any]:
        try:
            logger.warning(f"🚨 Emergency Exit Initiated for ALL")

            result = {
                "success": True,
                "closed_positions": [],
                "cancelled_orders": [],
                "errors": []
            }

            cancel_result = self.cancel_all_orders()
            payload = {
                "close_all_portfolio": True,
                "close_all_isolated": True,
                "user_id": 82942579
            }
            exit_positions = self.client.request(method="POST", path="/v2/positions/close_all", payload=payload, auth=True)
            result["cancelled_orders"] = cancel_result.get("cancelled_orders", [])

            logger.warning(f"✅ Emergency Exit Completed")
            return result

        except Exception as e:
            logger.critical(f"CRITICAL ERROR in Emergency Exit: {str(e)}")
            raise


