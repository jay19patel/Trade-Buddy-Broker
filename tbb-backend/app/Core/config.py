from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tradebuddy"
    SECRET_KEY: str = "jaypatel19key"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:5432/Tradebuddy"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRY: int = 86400 

    # class Config:
    #     env_file = ".env"

setting = Settings()