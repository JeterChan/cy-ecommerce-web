# CyWeb E-commerce Project

這是一個現代化、模組化單體架構（Modular Monolith）的電子商務平台系統。本專案採用前後端分離開發，並透過 Docker 實現一鍵式開發環境配置。

## 🚀 技術棧

### 後端 (Backend)
- **框架**: Python 3.12 + [FastAPI](https://fastapi.tiangolo.com/)
- **資料庫**: [PostgreSQL](https://www.postgresql.org/) (使用 SQLAlchemy Async 異步驅動)
- **快取/訊息隊列**: [Redis](https://redis.io/)
- **非同步任務**: [Celery](https://docs.celeryq.dev/) (處理 Email 寄送、排程任務等)
- **測試**: [Pytest](https://docs.pytest.org/)
- **驗證**: Pydantic v2

### 前端 (Frontend)
- **框架**: [Vue 3.5](https://vuejs.org/) (Composition API + TypeScript)
- **建構工具**: [Vite](https://vitejs.dev/)
- **狀態管理**: [Pinia](https://pinia.vuejs.org/)
- **樣式**: [Tailwind CSS](https://tailwindcss.com/) + [shadcn/ui (radix-vue)](https://www.radix-vue.com/)
- **多國語系**: vue-i18n

## ✨ 核心功能

- **商品模組**: 分類篩選、模糊搜尋、詳細資訊展示。
- **購物車系統**: 支援未登入 Redis 暫存與登入後的混合式同步機制。
- **原子結帳流程**:
  - 採用**悲觀鎖 (Pessimistic Locking)** 確保高併發下的庫存扣減一致性。
  - 具備防碰撞機制的訂單編號產生演算法。
  - 支援「貨到付款」與「銀行轉帳」等多種支付方式。
- **會員系統**: JWT 認證、個人資料編輯、訂單歷史查看。
- **訂單管理**: 支援訂單狀態追蹤與取消功能（取消時自動回補庫存）。
- **管理員後台**: 商品與分類的 CRUD 管理。

## 📦 快速開始

### 前置需求
- 安裝 [Docker](https://www.docker.com/) 與 [Docker Compose](https://docs.docker.com/compose/)

### 啟動開發環境

1. **配置環境變數**:
   在 `backend` 目錄下根據 `.env.example` 建立 `.env` 檔案。

2. **啟動容器**:
   ```bash
   docker-compose up --build
   ```
   啟動後，各服務位址如下：
   - **前端頁面**: `http://localhost:5173`
   - **後端 API**: `http://localhost:8000`
   - **API 文檔 (Swagger)**: `http://localhost:8000/docs`
   - **Flower (Celery 監控)**: `http://localhost:5555`

## 📂 專案結構

```text
├── backend/                # FastAPI 後端
│   ├── src/                # 原始碼 (依模組劃分: product, order, cart, auth...)
│   ├── tests/              # 單元與整合測試
│   ├── alembic/            # 資料庫遷移腳本
│   └── docker-compose.yml  # 容器配置
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── components/     # 共用組件
│   │   ├── stores/         # Pinia 狀態管理
│   │   ├── views/          # 頁面路由組件
│   │   └── services/       # API 介接層
├── specs/                  # 各階段開發規格書與設計文件
└── main.py                 # (Optional) 後端進入點
```

## 📜 開發規範

- 程式碼風格請遵循 PEP 8 (Python) 與 Prettier (TypeScript)。
- 提交代碼前請確保通過 `ruff` 檢查與所有自動化測試。
- 詳細的開發指令與技術細節請參考專案內部的 `GEMINI.md`。
