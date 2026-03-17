from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from infrastructure.database import init_redis, close_redis
from infrastructure import models
from infrastructure.config import settings

from shared.exceptions.base import DomainException
from shared.exceptions.common import (
    ResourceNotFoundException,
    BusinessRuleViolationException
)

from core.exceptions import (
    InvalidCredentialsError,
    ValidationError
)
from core.exception_handlers import (
    resource_not_found_exception_handler,
    business_rule_violation_exception_handler,
    domain_exception_handler,
    invalid_credentials_exception_handler,
    validation_exception_handler,
    pydantic_validation_exception_handler,
)

from modules.auth.presentation.routes import router as auth_router
from modules.product.presentation.routes import router as product_router
from modules.product.presentation.admin_routes import router as admin_product_router
from modules.product.presentation.category_routes import router as admin_category_router
from modules.cart.presentation.routes import router as cart_router
from modules.order.presentation.routes import router as order_router

@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        # 啟動時執行

        print("🚀 Application startup")
        from infrastructure.database import init_db
        await init_db()
        print("✅ Database tables initialized (only creating missing tables)")

        await init_redis()
        print("✅ Redis connection established")

        yield
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise
    finally:
        print("Application shutdown")
        await close_redis()
        print("Redis connection closed")
app = FastAPI(
    title="CyWeb E-commerce Backend",
    description="Modular Monolith API",
    version="1.0.0",
    docs_url=settings.DOCS_URL if settings.DOCS_URL else None,
    redoc_url=settings.REDOC_URL if settings.REDOC_URL else None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS 配置
# from infrastructure.config import settings (Moved to top)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# 如果環境變數中有設定前端網址，則加入許可清單
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 headers
)

# Pydantic 驗證例外（422）
app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)

# 特定領域異常
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)

# 3. 通用領域異常（後備匹配）
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(BusinessRuleViolationException, business_rule_violation_exception_handler)
app.add_exception_handler(DomainException, domain_exception_handler)

# Router 註冊
app.include_router(auth_router)
app.include_router(product_router, prefix="/api/v1")
app.include_router(admin_product_router, prefix="/api/v1")
app.include_router(admin_category_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")

@app.get("/api")
async def root():
    return {
        "message": "Welcome to the CyWeb E-commerce Backend API!",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
