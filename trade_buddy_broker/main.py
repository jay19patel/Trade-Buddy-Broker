from config import config
from core.ws_client import DeltaWebSocketClient
from services import OrdersService, PositionsService, TickerService


# WebSocket URL from config


def main() -> None:
    orders_service = OrdersService()
    positions_service = PositionsService()
    ticker_service = TickerService()

    callbacks = {
        "orders": orders_service.handle,
        "positions": positions_service.handle,
        "ticker": ticker_service.handle,
    }

    subscriptions = {
        "orders": ["all"],
        "positions": ["all"],
        "v2/ticker": ["BTCUSD", "ETHUSD"],
    }

    client = DeltaWebSocketClient(
        websocket_url=config.websocket_url,
        api_key=config.api_key,
        api_secret=config.api_secret,
        subscriptions=subscriptions,
        callbacks=callbacks,
        enable_heartbeat=True,
        heartbeat_interval_sec=config.heartbeat_interval_sec,
    )

    client.connect()


if __name__ == "__main__":
    main()
