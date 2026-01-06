import pytest
from src.shared.exceptions.base import DomainException
from src.shared.exceptions.common import (
    ResourceNotFoundException,
    BusinessRuleViolationException
)


def test_domain_exception():
    """測試基礎異常"""
    error = DomainException("測試錯誤")

    assert str(error) == "測試錯誤"
    assert error.message == "測試錯誤"


def test_resource_not_found_exception():
    """測試資源未找到異常"""
    error = ResourceNotFoundException("找不到使用者")

    assert isinstance(error, DomainException)
    assert str(error) == "找不到使用者"


def test_business_rule_violation_exception():
    """測試業務規則違反異常"""
    error = BusinessRuleViolationException("年齡必須大於 18")

    assert isinstance(error, DomainException)
    assert str(error) == "年齡必須大於 18"
