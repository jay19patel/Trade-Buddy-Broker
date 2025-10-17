"""
Redis Pub/Sub Subscriber Class
Listens to strategy results and batch completions in real-time with callback support
"""
import redis
import json
import logging
import os
from datetime import datetime
from typing import Callable, Optional, Dict, Any


# ============ LOGGING SETUP ============
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"event_{datetime.now().strftime('%Y%m%d')}.log")
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


class RedisSubscriber:
    """
    Redis Pub/Sub Subscriber with callback support and proper logging
    """

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 2, channel: str = 'stockanalysis:batch_complete'):
        """
        Initialize Redis subscriber

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            channel: Channel to subscribe to
        """
        self.host = host
        self.port = port
        self.db = db
        self.channel = channel
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        self.is_listening = False
    

    def add_callback_arguments(self, **kwargs) -> None:
        """
        Add arguments to the callback function
        """
        self.kwargs = kwargs
        logger.info(f"Callback function arguments added successfully: {kwargs}")

    def set_callback(self, callback_func: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Set callback function to handle received messages

        Args:
            callback_func: Function that takes (channel, data) as parameters
        """
        self.callback = callback_func
        logger.info("Callback function set successfully")
    
    def connect(self) -> None:
        """Connect to Redis, create pubsub object and subscribe to channel"""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )

            # Test connection
            self.redis_client.ping()

            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(self.channel)

            logger.info(f"Connected to Redis at {self.host}:{self.port} (db: {self.db})")
            logger.info(f"Subscribed to channel: {self.channel}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def start_listening(self) -> None:
        """
        Start listening for messages and call callback function when data is received
        """
        if not self.pubsub:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        if not self.callback:
            raise RuntimeError("No callback function set. Call set_callback() first.")

        self.is_listening = True
        logger.info("Started listening for real-time updates...")

        try:
            # Listen for messages
            for message in self.pubsub.listen():
                if not self.is_listening:
                    break

                if message['type'] == 'message':
                    try:
                        # Parse JSON data
                        data = json.loads(message['data'])
                        channel = message['channel']

                        logger.info(f"Received message from channel: {channel} Batch id: {data.get('data').get('batch_id')}")

                        # Call the callback function with channel and data
                        self.callback(channel, data, **self.kwargs)

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON data: {e}")
                        logger.error(f"Raw message: {message}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        logger.error(f"Raw message: {message}")

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping...")
        except Exception as e:
            logger.error(f"Unexpected error while listening: {e}")
        finally:
            self.stop_listening()
    
    def stop_listening(self) -> None:
        """Stop listening and cleanup resources"""
        self.is_listening = False

        if self.pubsub:
            self.pubsub.unsubscribe()
            self.pubsub.close()
            logger.info("Unsubscribed from all channels")

        if self.redis_client:
            self.redis_client.close()
            logger.info("Closed Redis connection")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_listening()

