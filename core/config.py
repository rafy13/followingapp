import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "Following App"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_USER: str = os.getenv("POSTGRES_USER", "admin")
    DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
    DATABASE_SERVER: str = os.getenv("POSTGRES_SERVER", "database")
    DATABASE_PORT: int = os.getenv("POSTGRES_PORT", 5432)
    DATABASE_NAME: str = os.getenv("POSTGRES_DB", "followingappdb")
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_NAME}"

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    TEST_USER_EMAIL = "test@example.com"

    MAIL_SERVICE_EMAIL=os.getenv("MAIL_SERVICE_EMAIL")
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
    MAIL_PORT=os.getenv("MAIL_PORT")
    MAIL_SERVER=os.getenv("MAIL_SERVER")

    BASE_URL = "http://localhost:8000"
    NEARBY_PLACE_MAX_DISTANCE = 1000


settings = Settings()