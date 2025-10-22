from pydantic_settings import BaseSettings, SettingsConfigDict
import redis


class Config(BaseSettings):
    # Delta Exchange API credentials
    api_key: str
    api_secret: str
    client_id: int

    # redis
    redis_url: str

    # WebSocket settings
    websocket_url: str = "wss://socket.india.delta.exchange"
    heartbeat_interval_sec: int = 30
    
    # MongoDB settings
    mongodb_url: str 
    mongodb_database: str = "trade_buddy"
    mongodb_positions_collection: str = "positions"
    mongodb_orders_collection: str = "orders"

    model_config = SettingsConfigDict(env_file=".env")


config = Config()
