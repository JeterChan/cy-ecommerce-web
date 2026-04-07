# src/infrastructure/config.py
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import computed_field, field_validator

# .env 位於 config.py 上三層（src/infrastructure/ → src/ → backend/）
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    # 1. 基礎設定
    PROJECT_NAME: str
    ENV: str

    # 2. 資料庫變數 (Pydantic 會自動讀取對應名稱的環境變數)
    DATABASE_URL: str | None = None  # 優先使用完整 URL
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ecommerce"

    # 3. Redis 設定
    REDIS_URL: str | None = None  # 優先使用完整 URL
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    REDIS_DECODE_RESPONSES: bool = True

    # 4. 購物車 Guest Token 設定
    GUEST_TOKEN_COOKIE_NAME: str
    GUEST_TOKEN_MAX_AGE: int
    GUEST_TOKEN_PATH: str
    GUEST_TOKEN_SECURE: bool
    GUEST_TOKEN_SAMESITE: str

    # 5. Email (Brevo) 設定
    BREVO_API_KEY: str
    BREVO_SENDER_EMAIL: str
    BREVO_SENDER_NAME: str
    FRONTEND_URL: str

    # 6. AWS S3 設定
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_S3_BUCKET: str | None = None
    AWS_S3_REGION: str = "ap-northeast-1"

    # 7. Documentation URL 設定
    DOCS_URL: str | None = "/api/docs"
    REDOC_URL: str | None = "/api/redoc"

    @field_validator("FRONTEND_URL")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    # 6. 自動組合成 SQLAlchemy 需要的連線字串
    @computed_field
    @property
    def database_url(self) -> str:
        """
        Builds the SQLAlchemy+asyncpg PostgreSQL connection URL from the current settings.

        Returns:
            str: Connection URL formatted as "postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}".
        """
        if self.DATABASE_URL:
            # Handle Render/Heroku postgres:// scheme for asyncpg
            return self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")

        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    @property
    def redis_url(self) -> str:
        """
        Returns the Redis connection URL.
        If REDIS_URL env var is set, uses it.
        Otherwise, constructs it from host/port/db/password.
        """
        if self.REDIS_URL:
            return self.REDIS_URL

        _password = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{_password}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    model_config = {
        # 優先讀取 .env 檔案，如果沒有則讀取系統環境變數
        "env_file": str(_ENV_FILE),
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",  # 忽略額外的環境變數（不報錯）
    }


# 實例化
settings = Settings()
