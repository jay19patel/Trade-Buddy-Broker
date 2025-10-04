from core.redis_ticker_store import RedisTickerStore

redis_ticker_store = RedisTickerStore()

class TickerService:
    def handle(self, message: dict) -> None:
        print("[TickerService]", message)
        redis_ticker_store.handle(message)
