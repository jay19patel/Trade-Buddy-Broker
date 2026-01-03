import redis
import json
from app.core.config import config

def send_test_data():
    """
    Publish test data to Redis channel that main.py is listening to
    """
    # Create Redis client
    redis_client = redis.from_url(config.redis_url)

    # Test data
    test_data = {
        "type": "batch_complete",
        "data": {
            "batch_id": "68f12aff3dfa2eec623ca58a",
            "summary": {
                "total_symbols": 3,
                "total_strategies": 5,
                "total_tasks": 15
            },
            "total_results": 3,
            "results": [
                {
                    "symbol": "ETHUSD",
                    "strategies": [
                        {
                            "strategy_name": "EMA Crossover Strategy",
                            "symbol": "ETHUSD",
                            "signal_type": "SELL",
                            "confidence": 0.0,
                            "execution_time": 0.2759273052215576,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 0.0,
                            "created_at": "2025-10-16 17:27:27.059386+00:00",
                            "_id": "68f12aff27dca72d9a3ca58a",
                            "success": True
                        }
                    ]
                }
            ]
        }
    }

    # Publish to the channel
    channel = "stockanalysis:batch_complete"
    message = json.dumps(test_data)

    print(f"Publishing to channel: {channel}")
    result = redis_client.publish(channel, message)
    print(f"Message published successfully! Subscribers received: {result}")

    redis_client.close()


if __name__ == "__main__":
    send_test_data()
