import redis
import json
from app.config import config

def send_test_data():
    """
    Publish test data to Redis channel that main.py is listening to
    """
    # Create Redis client
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True
    )

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
                    "symbol": "VFYUSD",
                    "strategies": [
                        {
                            "strategy_name": "EMA Crossover Strategy",
                            "symbol": "VFYUSD",
                            "signal_type": "HOLD",
                            "confidence": 0.0,
                            "execution_time": 0.2759273052215576,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 0.0,
                            "created_at": "2025-10-16 17:27:27.059386+00:00",
                            "_id": "68f12aff27dca72d9a3ca58a",
                            "sucess": True
                        },
                        {
                            "strategy_name": "RSI Oversold/Overbought Strategy",
                            "symbol": "VFYUSD",
                            "signal_type": "HOLD",
                            "confidence": 0.0,
                            "execution_time": 0.27466297149658203,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 0.0,
                            "created_at": "2025-10-16 17:27:27.059303+00:00",
                            "_id": "68f12aff7a620e01da3ca58c",
                            "sucess": True
                        },
                        {
                            "strategy_name": "Bollinger Bands Mean Reversion Strategy",
                            "symbol": "VFYUSD",
                            "signal_type": "BUY",
                            "confidence": 0.85,
                            "execution_time": 0.2602965831756592,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 67500.50,
                            "created_at": "2025-10-16 17:27:27.047146+00:00",
                            "_id": "68f12aff8b680056ab3ca58a",
                            "sucess": True
                        },
                        {
                            "strategy_name": "MACD Convergence Divergence Strategy",
                            "symbol": "VFYUSD",
                            "signal_type": "BUY",
                            "confidence": 0.75,
                            "execution_time": 0.36953139305114746,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 67500.50,
                            "created_at": "2025-10-16 17:27:27.157807+00:00",
                            "_id": "68f12affcc5b501c1c3ca58b",
                            "sucess": True
                        },
                        {
                            "strategy_name": "Volume Breakout Strategy",
                            "symbol": "VFYUSD",
                            "signal_type": "HOLD",
                            "confidence": 0.0,
                            "execution_time": 0.3893008232116699,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 0.0,
                            "created_at": "2025-10-16 17:27:27.179676+00:00",
                            "_id": "68f12affc270aff2853ca58b",
                            "sucess": True
                        }
                    ]
                },
                {
                    "symbol": "PUMPUSD",
                    "strategies": [
                        {
                            "strategy_name": "EMA Crossover Strategy",
                            "symbol": "PUMPUSD",
                            "signal_type": "BUY",
                            "confidence": 0.90,
                            "execution_time": 0.2605619430541992,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 3500.25,
                            "created_at": "2025-10-16 17:27:27.052658+00:00",
                            "_id": "68f12affa35bc12cbe3ca58c",
                            "sucess": True
                        },
                        {
                            "strategy_name": "RSI Oversold/Overbought Strategy",
                            "symbol": "PUMPUSD",
                            "signal_type": "HOLD",
                            "confidence": 0.0,
                            "execution_time": 0.3476099967956543,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 0.0,
                            "created_at": "2025-10-16 17:27:27.141613+00:00",
                            "_id": "68f12affec63c340313ca58a",
                            "sucess": True
                        },
                        {
                            "strategy_name": "Bollinger Bands Mean Reversion Strategy",
                            "symbol": "PUMPUSD",
                            "signal_type": "HOLD",
                            "confidence": 0.0,
                            "execution_time": 0.3753986358642578,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 0.0,
                            "created_at": "2025-10-16 17:27:27.170632+00:00",
                            "_id": "68f12affcbee700a563ca58b",
                            "sucess": True
                        },
                        {
                            "strategy_name": "MACD Convergence Divergence Strategy",
                            "symbol": "PUMPUSD",
                            "signal_type": "HOLD",
                            "confidence": 0.0,
                            "execution_time": 0.25043630599975586,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 0.0,
                            "created_at": "2025-10-16 17:27:27.301804+00:00",
                            "_id": "68f12aff8b680056ab3ca58b",
                            "sucess": True
                        },
                        {
                            "strategy_name": "Volume Breakout Strategy",
                            "symbol": "PUMPUSD",
                            "signal_type": "BUY",
                            "confidence": 0.0,
                            "execution_time": 0.18190217018127441,
                            "timestamp": "2025-10-16T17:26:26.215781+00:00",
                            "price": 0.0,
                            "created_at": "2025-10-16 17:27:27.239263+00:00",
                            "_id": "68f12affa35bc12cbe3ca58d",
                            "sucess": True
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
