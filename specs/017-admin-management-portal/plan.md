# Implementation Plan: Admin Management Portal

**Branch**: `017-admin-management-portal` | **Date**: 2026-03-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/017-admin-management-portal/spec.md`

## Summary
本計畫將實作管理員專屬的後台管理入口。核心包含：(1) 登入後的自動身分偵測與跳轉邏輯；(2) 統一的 `AdminLayout`（包含導航側邊欄）；(3) 前後台快速切換功能；(4) 基於角色的路由保護機制。

## Technical Context

**Language/Version**: Python 3.12, TypeScript 5.x, Vue 3.5  
**Primary Dependencies**: FastAPI, Vue Router, Pinia, Lucide Icons, shadcn/ui  
**Storage**: PostgreSQL (Users table)  
**Testing**: Vitest  
**Target Platform**: Web
**Project Type**: Web application (Frontend + Backend)  
**Performance Goals**: 跳轉延遲 < 200ms  
**Constraints**: 必須嚴格執行 RBAC 權限校驗

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **高品質**: 使用 Vue Router 守衛確保安全性。 (✅ Pass)
- **可測試性**: 包含針對角色跳轉的驗證流程。 (✅ Pass)
- **MVP 優先**: 優先實作跳轉與基礎佈局，不包含複雜報表。 (✅ Pass)
- **避免過度設計**: 複用現有 Auth Store 的使用者角色資訊。 (✅ Pass)
- **正體中文優先**: 所有文件與 UI 提示均使用正體中文。 (✅ Pass)

## Project Structure

### Documentation (this feature)

```text
specs/017-admin-management-portal/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── openapi.yaml
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── layouts/
│   │   └── AdminLayout.vue    # 新增：後台統一佈局
│   ├── views/
│   │   ├── LoginView.vue      # 修改：加入跳轉邏輯
│   │   └── admin/
│   │       └── AdminDashboard.vue # 新增：管理員首頁
│   ├── components/
│   │   └── layout/
│   │       └── Navbar.vue     # 修改：加入後台入口連結
│   └── router/
│       └── index.ts           # 修改：強化導航守衛
```

**Structure Decision**: 採用專屬 Layout 與 View 的結構，將管理員功能模組化。

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
