# 研究與技術決策: 使用者驗證

**功能分支**: `006-user-auth`
**日期**: 2026年1月7日

## 核心技術堆疊

### 1. 語言與框架
- **決策**: Python 3.12 + FastAPI
- **理由**: 
  - 使用者指定。
  - Python 3.12 提供更好的性能與型別提示支援。
  - FastAPI 是現代、高效能且原聲支援非同步的 Web 框架，完美整合 Pydantic 與 OpenAPI。

### 2. 資料庫與 ORM
- **決策**: SQLAlchemy 2.0 + Alembic (PostgreSQL)
- **理由**:
  - 使用者指定。
  - SQLAlchemy 2.0 提供統一的 AsyncIO 支援與更現代的語法。
  - Alembic 是 SQLAlchemy 的標準遷移工具，管理資料庫綱要變更。

### 3. 驗證與安全性
- **決策**: OAuth2 (Password Flow) + JWT + Passlib (Bcrypt)
- **理由**:
  - **JWT (JSON Web Tokens)**: 無狀態驗證，適合前後端分離架構 (Vue.js + FastAPI)。
  - **OAuth2 Password Flow**: 標準的登入流程，FastAPI 內建支援 (`OAuth2PasswordBearer`)。
  - **Passlib + Bcrypt**: 行業標準的密碼雜湊方案，安全且抗彩虹表攻擊。
  - **Pydantic v2**: 用於資料驗證與序列化，性能優於 v1。

## 實作細節研究

### 記住我 (Remember Me)
- **決策**: 長效期 JWT 或 Refresh Token
- **分析**: 
  - 傳統 Session cookie 也可以，但在 JWT 架構下，通常使用 Refresh Token 模式。
  - 若為了簡化 MVP，可發行較長效期的 Access Token (如 30 天) 給勾選「記住我」的使用者，或使用標準 Access (短效) + Refresh (長效) Token 機制。
  - **MVP 選擇**: 考量到 MVP 原則，我們將採用 **Access Token + Refresh Token** 模式。
    - 一般登入：Access Token (15-30分鐘), Refresh Token (Session/1天)。
    - 記住我：Refresh Token 效期延長至 30 天。
    - 前端需實作 Token 刷新邏輯。

### 架構設計
- **分層架構**:
  - `domain/`: 實體 (Entity) 定義。
  - `infrastructure/`: 資料庫模型 (SQLAlchemy Models)、Repository 實作。
  - `modules/auth/`: 認證相關邏輯 (Service)、API 路由 (Router)、Schemas (Pydantic)。
  - `shared/`: 共用工具 (Password Helper, JWT Handler)。

## 替代方案考量
- **Django**: 功能完整但過重，且專案已選定 FastAPI。
- **Session Auth**: 對於 SPA (Vue.js) 較不靈活，且需處理 CSRF。JWT 相對簡單且適合 API 導向。
