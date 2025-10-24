import json
import time
import hmac
import hashlib
import signal
import sys
from typing import Callable, Dict, List, Optional
import websocket
from .logger import get_websocket_logger

# Initialize centralized logger
logger = get_websocket_logger()


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
        self._should_reconnect = True
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 10
        self._reconnect_delay = 5  # seconds
        self._is_connected = False
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.disconnect()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

    def connect(self) -> None:
        """Connect to WebSocket with automatic reconnection"""
        try:
            while self._should_reconnect and self._reconnect_attempts < self._max_reconnect_attempts:
                try:
                    logger.info(f"Connecting to WebSocket (Attempt {self._reconnect_attempts + 1}/{self._max_reconnect_attempts})")
                    self._ws_app = websocket.WebSocketApp(
                        self.websocket_url,
                        on_open=self._on_open,
                        on_message=self._on_message,
                        on_error=self._on_error,
                        on_close=self._on_close,
                    )
                    
                    # Run with ping/pong for better connection monitoring
                    self._ws_app.run_forever(
                        ping_interval=30,  # Send ping every 30 seconds
                        ping_timeout=10,   # Wait 10 seconds for pong
                        ping_payload="ping"
                    )
                    
                except KeyboardInterrupt:
                    logger.info("KeyboardInterrupt received, stopping...")
                    self.disconnect()
                    break
                except Exception as e:
                    logger.error(f"WebSocket connection failed: {e}")
                    self._reconnect_attempts += 1
                    if self._reconnect_attempts < self._max_reconnect_attempts and self._should_reconnect:
                        logger.info(f"Reconnecting in {self._reconnect_delay} seconds...")
                        time.sleep(self._reconnect_delay)
                    else:
                        logger.error("Max reconnection attempts reached. Stopping.")
                        break
            
            if not self._should_reconnect:
                logger.info("WebSocket reconnection stopped by user")
                
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received in main loop, stopping...")
            self.disconnect()
        except Exception as e:
            logger.error(f"Unexpected error in connect: {e}")
            self.disconnect()
    
    def disconnect(self) -> None:
        """Disconnect WebSocket and stop reconnection"""
        logger.info("Initiating WebSocket disconnect...")
        self._should_reconnect = False
        
        if self._ws_app:
            try:
                # Close the WebSocket connection
                self._ws_app.close()
                self._is_connected = False
                logger.info("WebSocket disconnected successfully")
            except Exception as e:
                logger.error(f"Error during WebSocket disconnect: {e}")
        
        # Reset connection state
        self._reconnect_attempts = 0

    # --------------------------- Event Handlers --------------------------- #
    def _on_open(self, ws: websocket.WebSocketApp) -> None:
        logger.info("Socket opened")
        self._is_connected = True
        self._reconnect_attempts = 0  # Reset reconnection attempts on successful connection
        self._send_authentication(ws)

    def _on_error(self, ws: websocket.WebSocketApp, error) -> None:
        logger.error(f"Socket Error: {error}")

    def _on_close(self, ws: websocket.WebSocketApp, close_status_code, close_msg) -> None:
        logger.info(f"Socket closed with status: {close_status_code} and message: {close_msg}")
        self._is_connected = False
        
        if self._should_reconnect and self._reconnect_attempts < self._max_reconnect_attempts:
            logger.info("Connection lost, will attempt to reconnect...")
        else:
            logger.info("Connection closed and reconnection disabled")

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
                action = msg.get("action")
                logger.info(f"Orders update received - Action: {action}")

                # For snapshot: pass the result array
                if action == "snapshot":
                    self.callbacks["orders"](msg.get("result", []))
                # For create/delete: pass the order data as a single item list
                else:
                    self.callbacks["orders"]([msg])
            else:
                logger.warning("Orders Callback: Not Available")
            return

        # Positions
        if msg_type == "positions":
            if self.callbacks["positions"]:
                action = msg.get("action")
                logger.info(f"Positions update received - Action: {action}")

                # For snapshot: pass the result array
                if action == "snapshot":
                    self.callbacks["positions"](msg.get("result", []))
                # For create/delete: pass the position data as a single item list
                else:
                    self.callbacks["positions"]([msg])
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

