# CyWeb E-commerce Project

這是一個現代化、模組化單體架構（Modular Monolith）的電子商務平台系統。本專案採用前後端分離開發，並透過 Docker 實現一鍵式開發環境配置。

## 🌐 線上預覽

本專案已正式部署上線，歡迎直接瀏覽：

**[https://cy-ecommerce-web-frontend.vercel.app/](https://cy-ecommerce-web-frontend.vercel.app/)**

---

## 🚀 技術棧

### 後端 (Backend)
- **框架**: Python 3.12 + [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
- **資料庫**: [PostgreSQL 15](https://www.postgresql.org/) (SQLAlchemy 2.0 Async + asyncpg 驅動)
- **快取/訊息隊列**: [Redis 7](https://redis.io/)
- **非同步任務**: [Celery 5](https://docs.celeryq.dev/) (Email 寄送、購物車同步、排程清理)
- **任務監控**: [Flower](https://flower.readthedocs.io/)
- **資料庫遷移**: [Alembic](https://alembic.sqlalchemy.org/)
- **驗證**: Pydantic v2 + pydantic-settings
- **認證**: PyJWT + Bcrypt (passlib)
- **檔案儲存**: AWS S3 (Boto3)
- **Email**: [Brevo](https://www.brevo.com/) API
- **測試**: Pytest + pytest-asyncio + httpx
- **壓力測試**: [k6](https://k6.io/)（併發搶購壓力測試）
- **程式碼品質**: Ruff + Black

### 前端 (Frontend)
- **框架**: [Vue 3.5](https://vuejs.org/) (Composition API + TypeScript)
- **建構工具**: [Vite 7](https://vitejs.dev/)
- **狀態管理**: [Pinia 3](https://pinia.vuejs.org/)
- **路由**: Vue Router 4
- **HTTP 客戶端**: Axios 1（含 JWT 自動刷新攔截器）
- **UI 元件**: [Radix Vue](https://www.radix-vue.com/) (shadcn/ui 移植)
- **樣式**: [Tailwind CSS 3](https://tailwindcss.com/) + tailwind-merge + CVA
- **圖示**: Lucide Vue Next
- **表單驗證**: VeeValidate 4 + Zod
- **多國語系**: vue-i18n 11（繁體中文）
- **日期處理**: date-fns 4
- **測試**: Vitest + Vue Test Utils

### 部署 (Deployment)
- **前端**: [Vercel](https://vercel.com/)（SPA rewrite 規則）
- **後端**: [Render](https://render.com/)（含健康檢查，容器啟動自動執行 Migration）

---

## ✨ 核心功能

- **商品模組**: 分類篩選、模糊搜尋、多圖片展示、庫存管理。
- **購物車系統**: 支援訪客 Redis 暫存與登入後 PostgreSQL 混合式同步機制（HybridCartRepository）。
- **原子結帳流程**:
  - **Redis 預扣庫存**：使用 `DECRBY` 原子操作在進入 DB 事務前過濾庫存不足的請求，大幅降低高併發回應時間。
  - **悲觀鎖 (Pessimistic Locking)**（`SELECT ... FOR UPDATE`）作為最終防線，確保庫存扣減一致性。
  - 雙重保障機制：Redis 預扣 + DB 悲觀鎖，兼顧效能與資料正確性。
  - 具備防碰撞機制的日期前綴訂單編號產生演算法。
  - 支援「貨到付款」與「銀行轉帳」等多種支付方式。
- **會員系統**: JWT 雙 Token 認證（Access + Refresh）、個人資料編輯、Email 變更驗證、帳號刪除（軟刪除 + 定期硬刪除）。
- **訂單管理**: 訂單狀態追蹤、取消功能（取消時自動回補庫存）、收件人資訊管理。
- **管理員後台**: 商品與分類的 CRUD 管理、訂單狀態管理、儀表板統計數據。
- **非同步任務**: Email 寄送、購物車同步、過期帳號清理（每 24 小時）。

---

## 📦 快速開始

### 前置需求
- 安裝 [Docker](https://www.docker.com/) 與 [Docker Compose](https://docs.docker.com/compose/)

### 啟動開發環境

1. **配置環境變數**:
   在 `backend` 目錄下根據 `.env.example` 建立 `.env` 檔案。

2. **啟動容器**:
   ```bash
   cd backend
   docker compose up --build
   ```
   啟動後，各服務位址如下：
   - **前端頁面**: `http://localhost:5173`
   - **後端 API**: `http://localhost:8000`
   - **API 文檔 (Swagger)**: `http://localhost:8000/api/docs`
   - **Flower (Celery 監控)**: `http://localhost:5555`

3. **（可選）填入測試資料**:
   ```bash
   cd backend
   bash scripts/seed.sh
   ```

### 🗄️ 資料庫遷移（Dev / Production）

- **Dev 環境**: 容器啟動時不自動執行 Alembic，有新 Migration 時手動執行：
  ```bash
  cd backend
  docker compose --profile tools run --rm migrate
  ```
  `migrate` 服務會自動偵測舊 DB 已有資料表但無 `alembic_version` 的情況，先 `stamp` 基線再 `upgrade`，避免 `DuplicateTableError`。

- **Production 環境**: 由 `backend/start.sh` 在啟動前自動執行 `alembic upgrade head`，再啟動 API。

---

## 📂 專案結構

```text
├── backend/                         # FastAPI 後端
│   ├── src/
│   │   ├── modules/                 # 業務模組（Clean Architecture）
│   │   │   ├── auth/               # 認證與會員
│   │   │   ├── product/            # 商品與分類
│   │   │   ├── cart/               # 購物車
│   │   │   └── order/              # 訂單
│   │   ├── infrastructure/         # 跨模組基礎設施
│   │   │   ├── database.py         # 非同步 SQLAlchemy 連線
│   │   │   ├── stock_redis_service.py # Redis 庫存預扣服務
│   │   │   ├── celery_app.py       # Celery 設定
│   │   │   ├── s3.py               # AWS S3 整合
│   │   │   └── tasks/              # 跨模組 Celery 任務
│   │   ├── core/                   # 安全工具（JWT、密碼雜湊）
│   │   └── main.py                 # FastAPI 入口
│   ├── tests/                      # 單元與整合測試
│   ├── alembic/                    # 資料庫遷移腳本
│   ├── start.sh                    # Production 啟動腳本
│   └── docker-compose.yml          # 容器配置（API, DB, Redis, Celery, Flower）
├── frontend/                        # Vue 3 前端
│   ├── src/
│   │   ├── components/             # 共用元件（含 shadcn/ui）
│   │   ├── views/                  # 頁面路由元件
│   │   ├── stores/                 # Pinia 狀態管理
│   │   ├── services/               # API 介接層
│   │   ├── models/                 # Zod Schema 與 TypeScript 型別
│   │   ├── composables/            # Composition API 可重用邏輯
│   │   ├── i18n/                   # 多國語系（繁體中文）
│   │   ├── router/                 # Vue Router（含 Auth Guard）
│   │   └── lib/api.ts              # Axios 實例（含 JWT 自動刷新）
│   └── vercel.json                 # Vercel SPA 部署設定
└── specs/                          # 各階段開發規格書與設計文件
```

---

## 🏗️ 架構說明

### 後端：Clean Architecture（DDD 風格）

每個模組（`auth`、`product`、`cart`、`order`）遵循四層結構：

```
modules/{module}/
├── domain/           # 實體（Entity）、值物件（Value Object）、Repository 介面
├── application/      # Use Case、DTO
├── infrastructure/   # SQLAlchemy Model、Repository 實作、Celery Task
└── presentation/     # FastAPI 路由（routes.py、admin_routes.py）
```

**API 路由前綴：**
| 類型 | 前綴 |
|---|---|
| 認證 | `/api/v1/auth/*` |
| 顧客 API | `/api/v1/{products,cart,orders}` |
| 管理員 API | `/api/v1/admin/{products,orders,categories,dashboard}` |

### 認證機制

採用**雙 Token 策略**：
- **Access Token**: 有效期 24 小時（可設定）
- **Refresh Token**: 有效期 30 天
- 前端 Axios 攔截器自動偵測 401，呼叫 `/api/v1/auth/refresh` 換發，無感知刷新。

### 購物車系統

- **訪客**: Redis hash 儲存（以 guest_token 為 key）
- **已登入**: `HybridCartRepository`——寫入 Redis，透過 Celery 非同步同步至 PostgreSQL
- **登入後**: 本地 localStorage 購物車自動合併至後端

### Celery 任務隊列

| 隊列 | 用途 |
|---|---|
| `email_queue` | Email 寄送（驗證信、重設密碼等） |
| `cart_sync_queue` | Redis → PostgreSQL 購物車同步 |
| `default` | 清理與雜項任務 |

Beat 排程：每 24 小時自動硬刪除到期的軟刪除帳號。

### 結帳庫存保護：Redis 預扣 + DB 悲觀鎖

結帳流程採用**兩層庫存保護機制**，兼顧高併發效能與資料一致性：

```
用戶結帳請求
  │
  ▼
┌───────────────────────────┐
│ 第一層：Redis DECRBY 預扣  │ ← 原子操作，微秒級完成
│ 庫存 >= 0 → 通過          │   只有有效請求能通過
│ 庫存 < 0  → 立即拒絕      │   其餘在此直接返回 400
└───────────────────────────┘
  │ (僅少量請求通過)
  ▼
┌───────────────────────────┐
│ 第二層：DB SELECT FOR UPDATE │ ← 最終防線
│ 悲觀鎖保護庫存扣減          │   確保資料一致性
│ 失敗時回滾 Redis 庫存       │
└───────────────────────────┘
```

- **`StockRedisService`**：封裝 Redis 庫存操作（`init_stock`、`try_deduct`、`rollback`、`sync_stock`），支援 lazy init（key 不存在時自動從 DB 載入）。
- **庫存同步**：商品建立時初始化 Redis 庫存，Admin 調整庫存時同步更新 Redis。
- **多商品回滾**：購物車含多商品時，任一預扣失敗則回滾所有已預扣的商品。

---

## 📊 併發搶購壓力測試報告

使用 [k6](https://k6.io/) 模擬多用戶同時搶購僅剩 **10 個庫存**的商品，驗證庫存完整性與效能。

### 測試環境

| 項目 | 規格 |
|------|------|
| 機器 | macOS (Apple Silicon) |
| 容器化 | Docker Compose |
| API | FastAPI + Uvicorn (single worker) |
| 資料庫 | PostgreSQL 15, 連線池 `pool_size=5, max_overflow=10` |
| 快取 | Redis 7, `max_connections=50` |
| 測試工具 | k6 v1.6.1 |

### 測試結果

#### 優化前（純 DB 悲觀鎖）

| 併發用戶 (VU) | 成功訂單 | 庫存不足 | 異常錯誤 | 庫存完整性 | p50 (ms) | p95 (ms) | max (ms) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 100 | 10 | 90 | 0 | PASS | 926 | 968 | 1,024 |
| 500 | 10 | 490 | 0 | PASS | 609 | 785 | 1,180 |
| 1,000 | 10 | 990 | 0 | PASS | 1,511 | 1,978 | 4,044 |
| 2,000 | 10 | 1,990 | 0 | PASS | 2,455 | 3,269 | 3,418 |

#### 優化後（Redis 預扣 + DB 悲觀鎖）

| 併發用戶 (VU) | 成功訂單 | 庫存不足 | 異常錯誤 | 庫存完整性 | p50 (ms) | p95 (ms) | max (ms) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 100 | 10 | 90 | 0 | PASS | **304** | **1,194** | 1,196 |
| 500 | 10 | 490 | 0 | PASS | **503** | **604** | 1,227 |
| 1,000 | 10 | 990 | 0 | PASS | **721** | **956** | **1,186** |
| 2,000 | 10 | 1,990 | 0 | PASS | **1,530** | **2,066** | **2,127** |

#### 效能改善幅度

| VU | p50 改善 | max 改善 |
|---:|--------:|--------:|
| 100 | **-67%** | — |
| 500 | **-17%** | — |
| 1,000 | **-52%** | **-71%** |
| 2,000 | **-38%** | **-38%** |

### 關鍵結論

1. **庫存完整性**：所有測試等級（100 ~ 2,000 VU），成功訂單數恰好為 10，零超賣。
2. **效能提升**：Redis 預扣將大量注定失敗的請求在微秒級擋住，不再進入 DB 等待行鎖。2,000 VU 時 p50 從 2.5s 降到 1.5s。
3. **零異常錯誤**：所有請求均正確返回 201（成功）或 400（庫存不足），無 500 錯誤。

### 執行壓力測試

```bash
# 安裝 k6
brew install k6

# 啟動服務
cd backend
docker compose up --build -d

# 自動化多輪測試（預設 100 ~ 2000 VU）
./load_tests/run_load_test.sh

# 自訂測試等級
./load_tests/run_load_test.sh "100,500,1000"

# 自訂庫存數量
STOCK=20 ./load_tests/run_load_test.sh "100"
```

---

## 📜 開發規範

- Python 程式碼風格遵循 PEP 8，提交前通過 `ruff check .` 與 `black .`。
- TypeScript 程式碼風格遵循 Prettier 設定。
- 提交前確保通過 `pytest`（後端）與 `npm run test:unit`（前端）。

### 常用指令

```bash
# 後端
docker exec ecommerce_api alembic revision --autogenerate -m "描述"  # 產生 Migration
pytest                                                                 # 執行測試
ruff check .                                                           # Lint
black .                                                                # Format

# 前端
npm run dev          # 開發伺服器
npm run build        # Production 建構
npm run test:unit    # Vitest 單元測試
```
