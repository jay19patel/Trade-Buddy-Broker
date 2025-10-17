import json
import time
import hmac
import hashlib
from typing import Callable, Dict, List, Optional
import websocket
import logging
import os
from datetime import datetime


# ============ LOGGING SETUP ============
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"delta_websocket_{datetime.now().strftime('%Y%m%d')}.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Clear any existing handlers to avoid duplicates
logger.handlers = []

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter with file and function name
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class DeltaWebSocketClient:

    def __init__(
        self,
        websocket_url: str,
        api_key: str,
        api_secret: str,
        subscriptions: Optional[Dict[str, List[str]]] = None,
        orders_callback: Optional[Callable[[dict], None]] = None,
        positions_callback: Optional[Callable[[dict], None]] = None,
        ticker_callback: Optional[Callable[[dict], None]] = None,
    ):
        self.websocket_url = websocket_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.subscriptions = subscriptions or {}

        # Assign callbacks or mark as None
        self.callbacks = {
            "orders": orders_callback,
            "positions": positions_callback,
            "ticker": ticker_callback,
        }

        self._ws_app: Optional[websocket.WebSocketApp] = None

    def connect(self) -> None:
        self._ws_app = websocket.WebSocketApp(
            self.websocket_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._ws_app.run_forever()

    # --------------------------- Event Handlers --------------------------- #
    def _on_open(self, ws: websocket.WebSocketApp) -> None:
        logger.info("Socket opened")
        self._send_authentication(ws)

    def _on_error(self, ws: websocket.WebSocketApp, error) -> None:
        logger.error(f"Socket Error: {error}")

    def _on_close(self, ws: websocket.WebSocketApp, close_status_code, close_msg) -> None:
        logger.info(f"Socket closed with status: {close_status_code} and message: {close_msg}")

    def _on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        try:
            msg = json.loads(message)
            logger.info(f"Received message: {msg}")
        except json.JSONDecodeError:
            logger.error(f"Received non-JSON message: {message}")
            return

        # Route messages
        self._route_message(msg, ws)

    # ------------------------------ Helpers ------------------------------ #
    def _send_authentication(self, ws: websocket.WebSocketApp) -> None:
        method = "GET"
        timestamp = str(int(time.time()))
        path = "/live"
        signature_data = method + timestamp + path
        signature = self._generate_signature(self.api_secret, signature_data)
        logger.info("Sending authentication request")
        ws.send(
            json.dumps({
                "type": "auth",
                "payload": {
                    "api-key": self.api_key,
                    "signature": signature,
                    "timestamp": timestamp,
                }
            })
        )

    @staticmethod
    def _generate_signature(secret: str, message: str) -> str:
        return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    def _subscribe(self, ws: websocket.WebSocketApp, channel: str, symbols: List[str]) -> None:
        logger.info(f"Subscribing to channel: {channel} with symbols: {symbols}")
        ws.send(
            json.dumps({
                "type": "subscribe",
                "payload": {
                    "channels": [{"name": channel, "symbols": symbols}]
                }
            })
        )

    def _route_message(self, msg: dict, ws: websocket.WebSocketApp) -> None:
        msg_type = msg.get("type")

        # Authentication success -> subscribe to channels
        if msg_type == "success" and msg.get("message") == "Authenticated":
            logger.info("Authentication successful")
            for channel, symbols in self.subscriptions.items():
                self._subscribe(ws, channel, symbols)
            return

        # Orders
        if msg_type == "orders":
            if self.callbacks["orders"]:
                logger.info("Orders update received")
                self.callbacks["orders"](msg)
            else:
                logger.warning("Orders Callback: Not Available")
            return

        # Positions
        if msg_type == "positions":
            if self.callbacks["positions"]:
                logger.info("Positions update received")
                self.callbacks["positions"](msg)
            else:
                logger.warning("Positions Callback: Not Available")
            return

        # Ticker
        if msg_type in ("ticker", "v2/ticker"):
            if self.callbacks["ticker"]:
                logger.info("Ticker update received")
                self.callbacks["ticker"](msg)
            else:
                logger.warning("Ticker Callback: Not Available")
            return

        # Fallback: log any other messages
        logger.debug(f"Other Message: {msg}")




# def order_handle(message: dict) -> None:
#         print("-----------------[Order]-----------------")
#         results = message.get("result", [])
#         if not results:
#             print("No Orders found.")
#             return
#         print(f"Total Orders: {len(results)}")
#         for order in results:
#             print(order)
        

# def positions_handle(message: dict) -> None:
#     print("-----------------[Positions]-----------------")
#     results = message.get("result", [])
#     if not results:
#         print("No Positions found.")
#         return
#     print(f"Total Positions: {len(results)}")
#     for position in results:
#         print(position)



# subscriptions = {
#         "orders": ["all"],
#         "positions": ["all"]
#     }



# client = DeltaWebSocketClient(
#         websocket_url=config.websocket_url,
#         api_key=config.api_key,
#         api_secret=config.api_secret,
#         subscriptions=subscriptions,
#         orders_callback = order_handle ,
#         positions_callback = positions_handle,
#         ticker_callback = None,
#     )

# client.connect()