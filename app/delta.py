import json
import time
import hmac
import hashlib
from typing import Callable, Dict, List, Optional
import websocket


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
        print("Socket opened")
        self._send_authentication(ws)

    def _on_error(self, ws: websocket.WebSocketApp, error) -> None:
        print(f"Socket Error: {error}")

    def _on_close(self, ws: websocket.WebSocketApp, close_status_code, close_msg) -> None:
        print(f"Socket closed with status: {close_status_code} and message: {close_msg}")

    def _on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        try:
            msg = json.loads(message)
        except json.JSONDecodeError:
            print(f"Received non-JSON message: {message}")
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
            for channel, symbols in self.subscriptions.items():
                self._subscribe(ws, channel, symbols)
            return

        # Orders
        if msg_type == "orders":
            if self.callbacks["orders"]:
                self.callbacks["orders"](msg)
            else:
                print("Orders Callback: Not Available")
            return

        # Positions
        if msg_type == "positions":
            if self.callbacks["positions"]:
                self.callbacks["positions"](msg)
            else:
                print("Positions Callback: Not Available")
            return

        # Ticker
        if msg_type in ("ticker", "v2/ticker"):
            if self.callbacks["ticker"]:
                self.callbacks["ticker"](msg)
            else:
                print("Ticker Callback: Not Available")
            return

        # Fallback: print any other messages
        print("Other Message:", msg)
