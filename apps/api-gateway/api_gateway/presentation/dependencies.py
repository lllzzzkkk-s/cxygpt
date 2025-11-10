"""
表现层 - FastAPI 依赖
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .container import Container, get_container
from ..domain.entities import User
from ..utils.auth import TokenError, decode_access_token


def get_chat_completion_use_case(container: Container = Depends(get_container)):
    """获取聊天补全用例"""
    return container.chat_completion_use_case


def get_session_management_use_case(container: Container = Depends(get_container)):
    """获取会话管理用例"""
    return container.session_management_use_case


_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    container: Container = Depends(get_container),
) -> User:
    """获取当前登录用户"""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except TokenError as exc:  # pragma: no cover - 异常路径
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")

    user = await container.user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已停用")

    return user
