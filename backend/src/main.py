from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from infrastructure.database import recreate_all
from contextlib import asynccontextmanager

from shared.exceptions.base import DomainException
from shared.exceptions.common import (
    ResourceNotFoundException,
    BusinessRuleViolationException
)

from core.exceptions import (
    InvalidCredentialsError,
    ValidationError
)

from core.exceptions import (
    DuplicateEmailError,
    UserNotFoundError,
    InvalidCredentialsError,
    ValidationError
)
from core.exception_handlers import (
    pydantic_validation_exception_handler,
    resource_not_found_exception_handler,
    business_rule_violation_exception_handler,
    domain_exception_handler,
    invalid_credentials_exception_handler,
    validation_exception_handler
)

from modules.auth.api.router import router as auth_router

@asynccontextmanager
async def lifespan(application: FastAPI):
    # 啟動時執行
    await recreate_all()
    yield
app = FastAPI(
    title="CyWeb E-commerce Backend",
    description="Modular Monolith API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# 特定領域異常
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)

# 3. 通用領域異常（後備匹配）
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(BusinessRuleViolationException, business_rule_violation_exception_handler)
app.add_exception_handler(DomainException, domain_exception_handler)

# Router 註冊
app.include_router(auth_router)

@app.get("/api")
async def root():
    return {
        "message": "Welcome to the CyWeb E-commerce Backend API!",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

