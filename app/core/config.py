from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LogiPulse API"
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api/v1"

    MONGO_URI: str
    MONGO_DB_NAME: str = "logipulse"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.6-flash"

    LOG_LEVEL: str = "INFO"

    # Virgulle ayrilmis origin listesi, orn: "https://logipulse.example.com,http://localhost:8000"
    CORS_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"

    class Config:
        env_file = ".env"
        # MONGO_INITDB_ROOT_USERNAME/PASSWORD gibi bazi .env degerleri sadece
        # docker-compose.prod.yml'nin mongo servisini yapilandirmak icin var,
        # API bunlari okumaz. Bu yuzden bilinmeyen env degiskenleri yok sayilir.
        extra = "ignore"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
