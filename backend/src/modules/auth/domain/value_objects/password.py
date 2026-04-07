from dataclasses import dataclass
import re
from typing import List


@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self):
        error_msgs = self._validate()
        if error_msgs:
            raise ValueError(f"密碼不符合安全標準: {', '.join(error_msgs)}")

    def _validate(self) -> List[str]:
        error_msgs = []
        if len(self.value) < 8:
            error_msgs.append("密碼長度至少需要 8 個字元")
        if len(self.value) > 100:
            error_msgs.append("密碼長度不能超過 100 個字元")
        if not re.search(r"[A-Z]", self.value):
            error_msgs.append("密碼必須包含至少一個大寫字母")
        if not re.search(r"[a-z]", self.value):
            error_msgs.append("密碼必須包含至少一個小寫字母")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", self.value):
            error_msgs.append("密碼必須包含至少一個特殊字元")
        if re.search(r"\s", self.value):
            error_msgs.append("密碼不能包含空白字元")

        return error_msgs

    def __str__(self) -> str:
        return "********"
