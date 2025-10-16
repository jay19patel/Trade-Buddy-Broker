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

    def get_position(self, product_id: int) -> Dict[str, Any]:
        try:
            logger.info(f"Fetching position for product: {product_id}")
            return self.client.get_position(product_id)
        except Exception as e:
            logger.error(f"Error fetching position: {str(e)}")
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

    # ---------- Bracket Order ----------
    def create_bracket_order(
        self,
        product_id: int,
        size: int,
        side: str,
        entry_price: float,
        stoploss_price: float,
        target_price: float,
        leverage: int
    ) -> Dict[str, Any]:
        """
        Create a bracket order using place_order for all (entry, stoploss, target)
        """

        try:
            logger.info(f"Creating bracket order for {product_id}, Side: {side}, Size: {size}")
            logger.info(f"Entry: {entry_price}, SL: {stoploss_price}, Target: {target_price}, Leverage: {leverage}")

            # Set leverage
            self.client.set_leverage(product_id, str(leverage))
            opposite_side = 'sell' if side.lower() == 'buy' else 'buy'

            created_order_ids = []  # keep track for rollback on failure

            # 1️⃣ Entry Limit Order
            entry_order = self.client.place_order(
                product_id=product_id,
                size=size,
                side=side.lower(),
                order_type=DeltaOrderType.LIMIT,
                limit_price=str(entry_price),
            )
            # client returns parsed result, not nested under 'result'
            print(f"Entry order response : --------------------------------")
            print(entry_order)
            print(f"Entry order response : --------------------------------")
            entry_id = entry_order.get("id")
            if entry_id:
                created_order_ids.append(entry_id)
            logger.info(f"✅ Entry Order Created: {entry_id}")

            # 2️⃣ Stop Loss Order using dedicated API (market stop-loss)
            stop_order = self.client.place_stop_order(
                product_id=product_id,
                size=size,
                side=opposite_side,
                stop_price=str(stoploss_price),
                order_type=DeltaOrderType.MARKET,
                isTrailingStopLoss=False
            )
            print(f"Stop order response : --------------------------------")
            print(stop_order)
            print(f"Stop order response : --------------------------------")
            stop_id = stop_order.get("id")
            if stop_id:
                created_order_ids.append(stop_id)
            logger.info(f"✅ Stoploss Order Created: {stop_id}")

            # 3️⃣ Target Limit Order (reduce-only)
            target_order = self.client.place_order(
                product_id=product_id,
                size=size,
                side=opposite_side,
                order_type=DeltaOrderType.LIMIT,
                limit_price=str(target_price)
            )
            print(f"Target order response : --------------------------------")
            print(target_order)
            print(f"Target order response : --------------------------------")
            target_id = target_order.get("id")
            if target_id:
                created_order_ids.append(target_id)
            logger.info(f"✅ Target Order Created: {target_id}")

            return {
                "success": True,
                "entry_order_id": entry_id,
                "stoploss_order_id": stop_id,
                "target_order_id": target_id,
                "responses": {
                    "entry": entry_order,
                    "stoploss": stop_order,
                    "target": target_order
                }
            }

        except Exception as e:
            logger.error(f"❌ Error creating bracket order: {str(e)}")
            # Attempt rollback: cancel any orders that were created successfully
            try:
                # created_order_ids might be undefined if failure occurred before declaration
                for oid in locals().get('created_order_ids', []):
                    try:
                        self.cancel_order(product_id, oid)
                        logger.warning(f"Rolled back order id: {oid}")
                    except Exception as cancel_err:
                        logger.error(f"Failed to cancel order {oid}: {str(cancel_err)}")
            finally:
                raise

    # ---------- Emergency Exit ----------
    def emergency_exit(self, product_id: Optional[int] = None) -> Dict[str, Any]:
        try:
            logger.warning(f"🚨 Emergency Exit Initiated for {product_id if product_id else 'ALL'}")

            result = {
                "success": True,
                "closed_positions": [],
                "cancelled_orders": [],
                "errors": []
            }

            cancel_result = self.cancel_all_orders(product_id)
            result["cancelled_orders"] = cancel_result.get("cancelled_orders", [])

            if product_id:
                try:
                    position = self.get_position(product_id)
                    size = abs(position.get("result", {}).get("size", 0))
                    if size > 0:
                        side = "sell" if position["result"]["size"] > 0 else "buy"
                        close = self.client.place_order(
                            product_id=product_id,
                            size=size,
                            side=side,
                            order_type=DeltaOrderType.MARKET
                        )
                        result["closed_positions"].append(close)
                except Exception as e:
                    result["errors"].append(str(e))

            logger.warning(f"✅ Emergency Exit Completed")
            return result

        except Exception as e:
            logger.critical(f"CRITICAL ERROR in Emergency Exit: {str(e)}")
            raise
