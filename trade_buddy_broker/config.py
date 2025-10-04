from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # Delta Exchange API credentials
    api_key: str
    api_secret: str
    
    # Redis connection settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    
    # WebSocket settings
    websocket_url: str = "wss://socket.india.delta.exchange"
    heartbeat_interval_sec: int = 10
    
    # Redis ticker store settings
    ticker_redis_key: str = "ticker_data"
    ticker_max_items: int = 1000
    ticker_flush_interval_sec: int = 10

    model_config = SettingsConfigDict(env_file=".env")


config = Config()
