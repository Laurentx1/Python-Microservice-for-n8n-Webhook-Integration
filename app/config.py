from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    WEBHOOK_SECRET: str | None = None
    EXTERNAL_API_KEY: str | None = None
    EXTERNAL_API_URL: str = "https://api.example.com/data"
    REDIS_URL: str | None = None
    RETRY_ATTEMPTS: int = 5
    RETRY_BACKOFF_FACTOR: float = 2.0

    class Config:
        env_file = ".env"

settings = Settings()