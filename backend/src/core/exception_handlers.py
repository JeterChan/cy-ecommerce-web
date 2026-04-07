from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from shared.exceptions.base import DomainException
from shared.exceptions.common import (
    ResourceNotFoundException,
    BusinessRuleViolationException,
)
from core.exceptions import (
    DuplicateEmailError,
    UserNotFoundError,
    InvalidCredentialsError,
    ValidationError,
)


async def pydantic_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """處理 FastAPI RequestValidationError"""
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": list(error["loc"]),
            "msg": error["msg"],
            "type": error["type"],
        }
        if "ctx" in error and error["ctx"]:
            error_detail["ctx"] = {
                k: (
                    str(v)
                    if not isinstance(v, (str, int, float, bool, type(None)))
                    else v
                )
                for k, v in error["ctx"].items()
            }
        errors.append(error_detail)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": errors}
    )


# Domin exceptions handler
async def resource_not_found_exception_handler(
    request: Request, exc: ResourceNotFoundException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def business_rule_violation_exception_handler(
    request: Request, exc: BusinessRuleViolationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


# 特定異常處理器
async def invalid_credentials_exception_handler(
    request: Request, exc: InvalidCredentialsError
):
    """處理登入憑證無效錯誤"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """處理自訂驗證錯誤"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )
