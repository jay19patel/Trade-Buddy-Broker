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
    websocket_url: str 
    heartbeat_interval_sec: int
    
    # MongoDB settings
    mongodb_url: str 
    mongodb_database: str 
    mongodb_positions_collection: str 
    mongodb_orders_collection: str 

    model_config = SettingsConfigDict(env_file=".env")


config = Config()
