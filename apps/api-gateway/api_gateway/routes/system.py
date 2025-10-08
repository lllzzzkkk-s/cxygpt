"""
系统路由（健康检查、限额）
"""

from fastapi import APIRouter

from api_gateway.config import get_profile_name, settings
from api_gateway.models.schemas import HealthResponse, LimitsResponse

router = APIRouter(tags=["System"])


@router.get(
    "/healthz",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务是否正常运行",
)
async def health_check() -> HealthResponse:
    """健康检查"""
    return HealthResponse(ok=True)


@router.get(
    "/v1/limits",
    response_model=LimitsResponse,
    summary="获取限额",
    description="""
获取当前模式的限额配置。

前端应在启动时调用此接口，并根据返回值动态调整 UI 上限。

**错误码说明**：
- `413`: 输入超过 `max_input_tokens`
- `429`: 超过 QPS 或 TPM 限制，请参考 `Retry-After` 头
- `503`: 队列已满或系统繁忙
    """,
)
async def get_limits() -> LimitsResponse:
    """获取限额"""
    return LimitsResponse(
        max_input_tokens=settings.MAX_INPUT_TOKENS,
        max_output_tokens=settings.MAX_OUTPUT_TOKENS,
        rate_qps=settings.RATE_QPS,
        rate_tpm=settings.RATE_TPM,
        queue_size=settings.QUEUE_SIZE,
        single_user=settings.SINGLE_USER,
        profile=get_profile_name(settings),
    )
