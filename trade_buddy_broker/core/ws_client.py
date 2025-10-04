import json
import time
import hmac
import hashlib
from typing import Callable, Dict, List, Optional

import websocket


class DeltaWebSocketClient:
    """Class-based Delta Exchange WebSocket client with pluggable callbacks.

    Pass callbacks via the `callbacks` dict with optional keys:
      - "orders": Callable[[dict], None]
      - "positions": Callable[[dict], None]
      - "ticker": Callable[[dict], None]

    The client authenticates, subscribes to requested channels, and routes
    incoming messages to the relevant callback based on channel/topic.
    """

    def __init__(
        self,
        websocket_url: str,
        api_key: str,
        api_secret: str,
        subscriptions: Optional[Dict[str, List[str]]] = None,
        callbacks: Optional[Dict[str, Callable[[dict], None]]] = None,
        enable_heartbeat: bool = True,
        heartbeat_interval_sec: int = 10,
    ) -> None:
        self.websocket_url = websocket_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.subscriptions = subscriptions or {}
        self.callbacks = callbacks or {}
        self.enable_heartbeat = enable_heartbeat
        self.heartbeat_interval_sec = heartbeat_interval_sec

        self._ws_app: Optional[websocket.WebSocketApp] = None

    # ----------------------------- Public API ----------------------------- #
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
            message_json = json.loads(message)
        except json.JSONDecodeError:
            print(f"Received non-JSON message: {message}")
            return

        # After auth success, subscribe to configured channels
        if (
            message_json.get("type") == "success"
            and message_json.get("message") == "Authenticated"
        ):
            # Enable heartbeat (server pings) if configured
            if self.enable_heartbeat:
                ws.send(
                    json.dumps(
                        {
                            "type": "enable_heartbeat",
                            "interval": self.heartbeat_interval_sec,
                        }
                    )
                )

            # Perform subscriptions
            for channel, symbols in self.subscriptions.items():
                self._subscribe(ws, channel, symbols)
            return

        # Route messages to appropriate callbacks
        self._route_message_to_callback(message_json)

    # ------------------------------ Helpers ------------------------------ #
    def _send_authentication(self, ws: websocket.WebSocketApp) -> None:
        method = "GET"
        timestamp = str(int(time.time()))
        path = "/live"
        signature_data = method + timestamp + path
        signature = self._generate_signature(self.api_secret, signature_data)
        ws.send(
            json.dumps(
                {
                    "type": "auth",
                    "payload": {
                        "api-key": self.api_key,
                        "signature": signature,
                        "timestamp": timestamp,
                    },
                }
            )
        )

    @staticmethod
    def _generate_signature(secret: str, message: str) -> str:
        message_bytes = bytes(message, "utf-8")
        secret_bytes = bytes(secret, "utf-8")
        hash_obj = hmac.new(secret_bytes, message_bytes, hashlib.sha256)
        return hash_obj.hexdigest()

    def _subscribe(self, ws: websocket.WebSocketApp, channel: str, symbols: List[str]) -> None:
        payload = {
            "type": "subscribe",
            "payload": {
                "channels": [
                    {
                        "name": channel,
                        "symbols": symbols,
                    }
                ]
            },
        }
        ws.send(json.dumps(payload))

    def _route_message_to_callback(self, message_json: dict) -> None:
        # Route by top-level type per observed payloads
        msg_type = message_json.get("type")

        if msg_type == "orders" and "orders" in self.callbacks:
            self.callbacks["orders"](message_json)
            return

        if msg_type == "positions" and "positions" in self.callbacks:
            self.callbacks["positions"](message_json)
            return

        if msg_type in ("v2/ticker", "ticker") and "ticker" in self.callbacks:
            self.callbacks["ticker"](message_json)
            return

        # Optional: route heartbeats/subscriptions if provided
        if msg_type == "heartbeat" and "heartbeat" in self.callbacks:
            self.callbacks["heartbeat"](message_json)
            return

        if msg_type == "subscriptions" and "subscriptions" in self.callbacks:
            self.callbacks["subscriptions"](message_json)
            return

        # Fallback: print message if no route matched
        print(message_json)