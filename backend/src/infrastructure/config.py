# src/infrastructure/config.py
from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    # 1. 基礎設定
    PROJECT_NAME: str = "E-commerce Backend"
    ENV: str = "dev"  # dev, test, prod

    # 2. 資料庫變數 (Pydantic 會自動讀取對應名稱的環境變數)
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432 # 這裡強制規定要是數字
    DB_NAME: str = "ecommerce_db"

    # 3. 自動組合成 SQLAlchemy 需要的連線字串
    @computed_field
    @property
    def database_url(self) -> str:
        # 如果是 Docker 內部通訊，或者是外部連線，格式統一處理
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {
        # 優先讀取 .env 檔案，如果沒有則讀取系統環境變數
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }

# 實例化
settings = Settings()