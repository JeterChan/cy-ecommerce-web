from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
# load environment variables
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
# 延長 Access Token 過期時間從 30 分鐘到 24 小時
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))  # 24 hours
# 延長 Refresh Token 過期時間從 7 天到 30 天
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30))

# 密碼處理
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Determine whether a plaintext password matches a stored hashed password.
    
    Parameters:
    	plain_password (str): Plaintext password to verify.
    	hashed_password (str): Stored hashed password to compare against.
    
    Returns:
    	bool: `True` if `plain_password` matches `hashed_password`, `False` otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

# 註冊時使用, 將明文的密碼加密, 未來用於儲存在資料庫
def get_password_hash(password: str) -> str:
    """
    Generate a secure hashed representation of a password for storage.
    
    Parameters:
        password (str): Plaintext password to hash.
    
    Returns:
        str: Hashed password suitable for storage.
    """
    return pwd_context.hash(password)

# Token 生成
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token containing the provided claims and an expiration.
    
    Parameters:
        data (dict): Claims to include in the token (e.g., "sub" for subject, "user_id", "role").
        expires_delta (Optional[timedelta]): Optional custom time span to set the token's expiration; when omitted a default expiry is used.
    
    Returns:
        encoded_jwt (str): Encoded JWT string containing the provided claims plus an "exp" claim and a "type" set to "access".
    """
    # data 內容
    # data = {
    #   "sub" -> 用戶識別
    #   "user_id" -> 用戶 ID
    #   "role" -> 角色權限
    # }
    to_encode = data.copy() # 複製輸入資料 (避免修改原始資料）
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 加入標準 JWT 聲明
    to_encode.update({
        "exp": expire, # 過期時間
        "type": "access" # 自訂欄位, 區分 token 類型
    })

    # 編碼為 JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """
    Create a refresh JWT that includes the provided claims and an expiration.
    
    Parameters:
        data (dict): Claims to include in the token payload.
    
    Returns:
        refresh_token (str): Encoded JWT string containing the provided claims plus an "exp" claim set to the refresh expiry and a "type" claim with value "refresh".
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token 驗證
def verify_token(token :str, token_type: str = "access") -> Optional[dict]:
    """
    Validate a JWT and return its decoded payload when its `type` claim matches the expected token_type.
    
    Parameters:
        token (str): The JWT string to validate and decode.
        token_type (str): Expected value of the payload's `type` claim (defaults to "access").
    
    Returns:
        dict: Decoded JWT payload if the token is valid and its `type` claim equals `token_type`.
        `None`: If the token is invalid, cannot be decoded, or the `type` claim does not match.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None