FROM python:3.12-slim

# 設定 maintainer 資訊
LABEL authors="jeterchan"

# 設定 container 的工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# 安裝系統相依套件
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 複製專案程式碼與設定檔
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY src/ ./src/
COPY start.sh .
RUN chmod +x start.sh

# 開放應用程式埠口
EXPOSE 10000

# 健康檢查 (Render 會使用這個檢查服務是否存活)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/api/health || exit 1

# 啟用命令：使用 start.sh 腳本啟動
CMD ["./start.sh"]
