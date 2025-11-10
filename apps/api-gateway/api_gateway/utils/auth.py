"""JWT 认证工具"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt

from api_gateway.config import settings


class TokenError(Exception):
    """令牌解析错误"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """解析访问令牌"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:  # pragma: no cover - 异常路径
        raise TokenError("Invalid or expired token") from exc
    return payload
