from dataclasses import dataclass
import re
from typing import List


@dataclass(frozen=True)
class Email:
    """
    Email Value Object

    職責：
    - 驗證 Email 格式的有效性
    - 規範化 Email（統一轉為小寫）
    - 確保 Email 在建立時就是有效的
    """
    value: str

    def __post_init__(self):
        """建立後立即驗證"""
        error_msgs = self._validate()
        if error_msgs:
            raise ValueError(f"Email 格式不符合標準: {', '.join(error_msgs)}")

        # 規範化：統一轉為小寫
        object.__setattr__(self, 'value', self.value.lower().strip())

    def _validate(self) -> List[str]:
        """
        驗證 Email 格式

        規則：
        - 不能為空
        - 長度限制（最大 255 字元）
        - 必須符合基本 Email 格式
        """
        error_msgs = []

        if not self.value or not self.value.strip():
            error_msgs.append("Email 不能為空")
            return error_msgs

        email = self.value.strip()

        if len(email) > 255:
            error_msgs.append("Email 長度不能超過 255 個字元")

        # 基本 Email 格式驗證（簡化版）
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            error_msgs.append("Email 格式不正確")

        return error_msgs

    def __str__(self) -> str:
        """返回標準化的 Email 字串"""
        return self.value

    def __repr__(self) -> str:
        return f"Email('{self.value}')"

