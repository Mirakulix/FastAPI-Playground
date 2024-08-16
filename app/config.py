import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    azure_openai_key: str = os.getenv("AZURE_OPENAI_KEY")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int = int(os.getenv("REDIS_DB", 0))
    log_file: str = os.getenv("LOG_FILE", "app.log")
    log_max_bytes: int = int(os.getenv("LOG_MAX_BYTES", 5242880))
    log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", 5))

settings = Settings()
