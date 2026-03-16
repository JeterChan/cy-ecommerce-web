"""
測試全域 conftest

在 pytest 收集測試之前（模組 import 之前）執行兩項設定：
  1. 載入 .env.test 中的測試專用環境變數（TEST_DB_* 等）
  2. 修正 .env 中含有 inline comment 的設定值，使 pydantic-settings
     的 Settings() 可以正確解析 int / bool 型別。

.env 中的問題行（inline comment 導致型別錯誤）：
  GUEST_TOKEN_MAX_AGE=604800# 7 days in seconds  → int 解析失敗
  GUEST_TOKEN_SECURE=false# Set to true in production  → bool 解析失敗
"""

import os
from pathlib import Path

# 載入 .env.test（測試專用 DB 帳密等），不覆蓋已設定的系統環境變數
_env_test_path = Path(__file__).parent.parent / ".env.test"
if _env_test_path.exists():
    with open(_env_test_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

# 以系統環境變數覆蓋 .env 中無法解析的值（系統 env 優先於 env_file）
os.environ.setdefault("GUEST_TOKEN_MAX_AGE", "604800")
os.environ.setdefault("GUEST_TOKEN_SECURE", "false")
