from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import redis


class Config(BaseSettings):
    # Delta Exchange API credentials
    base_url: str
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
    
    # Trade Calculator settings
    trade_percent: float
    risk_ratio: float
    reward_ratio: float

    @field_validator('trade_percent', mode='before')
    @classmethod
    def parse_trade_percent(cls, v):
        """Convert '30' or '30%' to float value"""
        if isinstance(v, str):
            v = v.strip().rstrip('%')
        return float(v)
    
    @field_validator('risk_ratio', mode='before')
    @classmethod
    def parse_risk_ratio(cls, v):
        """Convert '1%' to 0.01"""
        if isinstance(v, str):
            v = v.strip().rstrip('%')
            return float(v) / 100
        return v
    
    @field_validator('reward_ratio', mode='before')
    @classmethod
    def parse_reward_ratio(cls, v):
        """Convert '3%' to 0.03"""
        if isinstance(v, str):
            v = v.strip().rstrip('%')
            return float(v) / 100
        return v

    model_config = SettingsConfigDict(env_file=".env")


config = Config()
