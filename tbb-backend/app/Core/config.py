from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tradebuddy"
    SECRET_KEY: str = "jaypatel19key"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:root@localhost:5432/Tradebuddy"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRY: int = 86400  # Seconds 
    HOST_NAME: str = "127.0.0.1"
    HOST_PORT: int = 8080
    USE_HTTPS: bool = True

    @property
    def HOST_URL(self):
        return f"http://{self.HOST_NAME}:{self.HOST_PORT}/"
    # class Config:
    #     env_file = ".env"

setting = Settings()