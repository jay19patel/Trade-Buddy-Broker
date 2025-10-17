from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # Delta Exchange API credentials
    api_key: str
    api_secret: str

    client_id: int

    # WebSocket settings
    websocket_url: str = "wss://socket.india.delta.exchange"
    heartbeat_interval_sec: int = 30
    


    model_config = SettingsConfigDict(env_file=".env")


config = Config()
