# Implementation Plan: Backend Cart Merge System

**Branch**: `009-cart-merge-system` | **Date**: 2026-01-25 | **Spec**: [specs/009-cart-merge-system/spec.md](../spec.md)
**Input**: Feature specification from `/specs/009-cart-merge-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

本功能實作後端購物車系統，區分訪客與會員購物車。主要功能包含為訪客與會員工作階段新增/更新/移除項目，以及在成功登入後將訪客購物車項目合併至會員購物車的邏輯。將使用 Redis 作為高效能購物車儲存。

## Technical Context

**Language/Version**: Python 3.12 (Constraint)
**Primary Dependencies**: FastAPI, Redis, Pydantic
**Storage**: Redis (for Cart data), PostgreSQL (for persistent Member Cart)
**Testing**: pytest
**Target Platform**: Linux server (Docker)
**Project Type**: Web API (Backend)
**Performance Goals**: 購物車操作 < 200ms
**Constraints**: 必須無縫處理訪客至會員的購物車合併。
**Scale/Scope**: 支援併發購物車操作；高效合併。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **High Quality**: 將使用 Pydantic 進行驗證與型別提示。
- [x] **Testability**: 合併與購物車操作邏輯將被隔離且可測試。
- [x] **MVP First**: 專注於核心購物車操作與合併邏輯。
- [x] **Avoid Overdesign**: 使用 Redis 以求速度；簡單的合併策略。
- [x] **Traditional Chinese**: 文件與註釋使用正體中文。

## Project Structure

### Documentation (this feature)

```text
specs/009-cart-merge-system/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── modules/
│   │   └── cart/             # New module
│   │       ├── api/          # Routers
│   │       ├── domain/       # Business logic (Entities, Services)
│   │       └── infrastructure/ # Repositories (Redis implementation)
│   └── main.py               # App entry point (update to include cart router)
└── tests/
    └── modules/
        └── cart/             # Cart tests
```

**Structure Decision**: 遵循 `backend/src/modules` 中的現有模組化架構。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       |            |                                     |
