from .base import DomainException

class ResourceNotFoundException(DomainException):
    """ 當找不到請求的資源時拋出 """
    pass

class BusinessRuleViolationException(DomainException):
    """ 當業務規則被違反時拋出 """
    pass