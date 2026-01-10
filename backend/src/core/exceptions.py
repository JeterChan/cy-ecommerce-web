class DuplicateEmailError(Exception):
    """當 email 重複時拋出"""
    pass

class UserNotFoundError(Exception):
    """當user不存在時拋出"""
    pass

class InvalidCredentialsError(Exception):
    """當登入憑證無效時拋出"""
    pass