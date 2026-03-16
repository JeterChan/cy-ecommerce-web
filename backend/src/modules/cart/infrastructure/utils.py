"""
購物車工具模組
提供訪客 Token 產生與驗證功能
"""
import uuid
import secrets
from typing import Optional
from fastapi import Response, Request

from infrastructure.config import settings


# === 從配置讀取常數 ===
GUEST_TOKEN_COOKIE_NAME = settings.GUEST_TOKEN_COOKIE_NAME
GUEST_TOKEN_MAX_AGE = settings.GUEST_TOKEN_MAX_AGE
GUEST_TOKEN_PATH = settings.GUEST_TOKEN_PATH
GUEST_TOKEN_SECURE = settings.GUEST_TOKEN_SECURE
GUEST_TOKEN_SAMESITE = settings.GUEST_TOKEN_SAMESITE


def generate_guest_token() -> str:
    """
    生成訪客購物車識別 Token

    設計考量:
    1. 使用 UUID4 確保全域唯一性
    2. 加上 secrets token 增加隨機性
    3. 格式: guest_{uuid}_{random}

    Returns:
        str: 格式化的訪客 Token，例如 "guest_123e4567-e89b-12d3-a456-426614174000_a7b3c9"
    """
    guest_uuid = uuid.uuid4()
    random_suffix = secrets.token_hex(3)  # 6 個字元的隨機後綴
    return f"guest_{guest_uuid}_{random_suffix}"


def set_guest_token_cookie(response: Response, token: str) -> None:
    """
    將訪客 Token 設定為 HTTP-only Cookie

    安全性考量:
    1. httponly=True: 防止 JavaScript 存取 (XSS 防護)
    2. secure: 從配置讀取，生產環境應為 True (僅 HTTPS 傳輸)
    3. samesite: 從配置讀取，預設 "lax" (CSRF 防護)
    4. max_age: 從配置讀取，預設 7 天
    5. path: 從配置讀取，預設限制在 /api/cart 路徑

    Args:
        response: FastAPI Response 物件
        token: 訪客 Token 字串
    """
    response.set_cookie(
        key=GUEST_TOKEN_COOKIE_NAME,
        value=token,
        max_age=GUEST_TOKEN_MAX_AGE,
        path=GUEST_TOKEN_PATH,
        httponly=True,  # 防止 XSS
        secure=GUEST_TOKEN_SECURE,  # 從配置讀取
        samesite=GUEST_TOKEN_SAMESITE  # 從配置讀取
    )


def get_guest_token_from_cookie(request: Request) -> Optional[str]:
    """
    從 Cookie 中提取訪客 Token

    Args:
        request: FastAPI Request 物件

    Returns:
        Optional[str]: 訪客 Token，若不存在則回傳 None
    """
    return request.cookies.get(GUEST_TOKEN_COOKIE_NAME)


def validate_guest_token(token: Optional[str]) -> bool:
    """
    驗證訪客 Token 格式是否正確

    驗證規則:
    1. Token 不能為 None 或空字串
    2. 必須以 "guest_" 開頭
    3. 格式必須符合 guest_{uuid}_{random}

    Args:
        token: 待驗證的 Token

    Returns:
        bool: Token 格式是否有效
    """
    if not token:
        return False

    if not token.startswith("guest_"):
        return False

    # 驗證格式: guest_{uuid}_{random}
    parts = token.split("_")
    if len(parts) != 3:
        return False

    # 驗證 UUID 部分
    try:
        uuid.UUID(parts[1])  # 第二部分應該是有效的 UUID
    except ValueError:
        return False

    # 驗證隨機後綴 (應該是 6 個 hex 字元)
    random_part = parts[2]
    if len(random_part) != 6:
        return False

    try:
        int(random_part, 16)  # 確認是 hex 字串
    except ValueError:
        return False

    return True


def clear_guest_token_cookie(response: Response) -> None:
    """
    清除訪客 Token Cookie

    使用場景:
    1. 訪客登入成功後，購物車已合併至會員帳號
    2. 使用者手動清空購物車

    Args:
        response: FastAPI Response 物件
    """
    response.delete_cookie(
        key=GUEST_TOKEN_COOKIE_NAME,
        path=GUEST_TOKEN_PATH
    )


def get_or_create_guest_token(request: Request, response: Response) -> str:
    """
    取得現有的訪客 Token，若不存在則建立新的

    這是最常用的工具函式，在訪客購物車 API 中使用

    工作流程:
    1. 嘗試從 Cookie 中取得 Token
    2. 驗證 Token 格式
    3. 若無效或不存在，生成新的 Token 並設定 Cookie

    Args:
        request: FastAPI Request 物件
        response: FastAPI Response 物件

    Returns:
        str: 有效的訪客 Token
    """
    token = get_guest_token_from_cookie(request)

    if token and validate_guest_token(token):
        return token

    # Token 無效或不存在，生成新的
    new_token = generate_guest_token()
    set_guest_token_cookie(response, new_token)
    return new_token


# === Redis Key 生成工具 ===

def get_guest_cart_redis_key(guest_token: str) -> str:
    """
    生成訪客購物車的 Redis Key

    格式: cart:guest:{token}

    Args:
        guest_token: 訪客 Token

    Returns:
        str: Redis Key
    """
    return f"cart:guest:{guest_token}"


def get_member_cart_redis_key(user_id: uuid.UUID) -> str:
    """
    生成會員購物車的 Redis Key

    格式: cart:user:{uuid}

    Args:
        user_id: 會員 UUID

    Returns:
        str: Redis Key
    """
    return f"cart:user:{user_id}"

