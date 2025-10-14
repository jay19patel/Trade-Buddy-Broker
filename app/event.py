"""
Redis Pub/Sub Subscriber Class
Listens to strategy results and batch completions in real-time with callback support
"""
import redis
import json
import logging
from typing import Callable, Optional, Dict, Any


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
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler if not already exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def set_callback(self, callback_func: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Set callback function to handle received messages
        
        Args:
            callback_func: Function that takes (channel, data) as parameters
        """
        self.callback = callback_func
        self.logger.info("Callback function set successfully")
    
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
            
            self.logger.info(f"Connected to Redis at {self.host}:{self.port} (db: {self.db})")
            self.logger.info(f"Subscribed to channel: {self.channel}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
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
        self.logger.info("🎧 Started listening for real-time updates...")
        
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
                        
                        self.logger.info(f"📡 Received message from channel: {channel}")
                        
                        # Call the callback function with channel and data
                        self.callback(channel, data)
                        
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse JSON data: {e}")
                        self.logger.error(f"Raw message: {message}")
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
                        self.logger.error(f"Raw message: {message}")
                        
        except KeyboardInterrupt:
            self.logger.info("👋 Received interrupt signal, stopping...")
        except Exception as e:
            self.logger.error(f"Unexpected error while listening: {e}")
        finally:
            self.stop_listening()
    
    def stop_listening(self) -> None:
        """Stop listening and cleanup resources"""
        self.is_listening = False
        
        if self.pubsub:
            self.pubsub.unsubscribe()
            self.pubsub.close()
            self.logger.info("Unsubscribed from all channels")
        
        if self.redis_client:
            self.redis_client.close()
            self.logger.info("Closed Redis connection")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_listening()


def main():
    """
    Example usage of RedisSubscriber class
    """
    def my_callback(channel: str, data: Dict[str, Any]) -> None:
        """
        Example callback function
        
        Args:
            channel: Channel name where message was received
            data: Parsed JSON data from the message
        """
        print("=" * 80)
        print(f"📡 Channel: {channel}")
        print("-" * 80)
        print(json.dumps(data, indent=2))
        print("-" * 80)
    
    # Create subscriber instance
    subscriber = RedisSubscriber()
    
    try:
        # Connect to Redis (automatically subscribes to channel)
        subscriber.connect()
        
        # Set callback function
        subscriber.set_callback(my_callback)
        
        # Start listening
        subscriber.start_listening()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        subscriber.stop_listening()


if __name__ == "__main__":
    main()
