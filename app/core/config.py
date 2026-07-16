from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LogiPulse API"

    MONGO_URI: str
    MONGO_DB_NAME: str = "logipulse"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
