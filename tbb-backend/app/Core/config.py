from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tradebuddy"
    SECRET_KEY: str = "jaypatel19key"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:5432/tradebuddy"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRY: int = 86400
    HOST_NAME: str = "localhost"
    HOST_PORT: int = 8000
    USE_HTTPS: bool = True

    @property
    def HOST_URL(self):
        return f"http://{self.HOST_NAME}:{self.HOST_PORT}/"
    # class Config:
    #     env_file = ".env"

setting = Settings()