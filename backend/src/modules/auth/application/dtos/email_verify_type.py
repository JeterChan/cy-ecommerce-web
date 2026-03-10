from enum import Enum

class EmailVerifyType(str, Enum):
    OLD = "old"
    NEW = "new"
