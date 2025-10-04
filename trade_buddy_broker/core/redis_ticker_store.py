import redis
import json
import time
from typing import List, Dict
from config import config

class RedisTickerStore:
    def __init__(self):
        # Redis connection
        self.r = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                decode_responses=True,
                username="default",
                password=config.redis_password,
            )
        self.redis_key = config.ticker_redis_key
        self.max_items = config.ticker_max_items
        # Batch related
        self.batch: List[Dict] = []
        self.last_flush_epoch_sec = 0
        self.flush_interval_sec = config.ticker_flush_interval_sec

    def handle(self, message: dict) -> None:
        # Print essential info for visibility
        print("[TickerService]")
        print("Symbol:", message.get("symbol"))
        print("Last Price:", message.get("close") or message.get("mark_price"))
        print("High:", message.get("high"))
        print("Low:", message.get("low"))
        print("Volume:", message.get("volume"))
        print("Open Interest:", message.get("oi"))
        print("Funding Rate:", message.get("funding_rate"))
        print("Timestamp:", message.get("timestamp"))

        # Buffer into in-memory batch
        self.batch.append(message)

        # Flush every 10 seconds
        now = int(time.time())
        if now - self.last_flush_epoch_sec >= self.flush_interval_sec:
            self._flush_batch()

    def _flush_batch(self) -> None:
        if not self.batch:
            self.last_flush_epoch_sec = int(time.time())
            return

        # Convert batch to JSON lines for efficient push
        pipe = self.r.pipeline(transaction=False)
        for item in self.batch:
            pipe.lpush(self.redis_key, json.dumps(item))
        pipe.ltrim(self.redis_key, 0, self.max_items - 1)
        pipe.execute()

        # Reset batch and timestamp
        self.batch.clear()
        self.last_flush_epoch_sec = int(time.time())
