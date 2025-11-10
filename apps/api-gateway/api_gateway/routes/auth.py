"""认证相关路由"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from api_gateway.config import settings
from api_gateway.models.schemas import LoginRequest, LoginResponse, Token, UserProfile
from api_gateway.presentation.container import Container
from api_gateway.presentation.dependencies import get_container, get_current_user
from api_gateway.utils.auth import create_access_token
from api_gateway.utils.security import verify_password

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    payload: LoginRequest,
    container: Container = Depends(get_container),
) -> LoginResponse:
    """使用用户名和密码登录"""
    user = await container.user_repo.get_by_username(payload.username)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": user.id}, expires_delta=token_expires)

    return LoginResponse(access_token=access_token, token_type="bearer", user=UserProfile.model_validate(user))


@router.get("/me", response_model=UserProfile, summary="获取当前用户信息")
async def get_me(current_user=Depends(get_current_user)) -> UserProfile:
    """返回当前登录用户"""
    return UserProfile.model_validate(current_user)


@router.post("/refresh", response_model=Token, summary="刷新令牌")
async def refresh_token(current_user=Depends(get_current_user)) -> Token:
    """刷新访问令牌"""
    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": current_user.id}, expires_delta=token_expires)
    return Token(access_token=access_token)
