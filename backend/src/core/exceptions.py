from shared.exceptions.base import DomainException
from shared.exceptions.common import (
    ResourceNotFoundException,
    BusinessRuleViolationException
)

class DuplicateEmailError(BusinessRuleViolationException):
    """當 email 重複時拋出"""
    def __init__(self, email: str):
        super().__init__(f"Email {email} 已被使用")


class UserNotFoundError(ResourceNotFoundException):
    """當user不存在時拋出"""
    def __init__(self, identifier: str):
        super().__init__(f"使用者 {identifier} 不存在")

class InvalidCredentialsError(DomainException):
    """當登入憑證無效時拋出"""
    def __init__(self):
        super().__init__("帳號或密碼錯誤")

class ValidationError(DomainException):
    """當資料驗證失敗時拋出"""
    def __init__(self, message: str):
        super().__init__(message)