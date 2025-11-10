"""
聊天路由
"""

import asyncio
import time
import uuid
from collections.abc import AsyncGenerator

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from api_gateway.config import settings
from api_gateway.models.schemas import (
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ErrorResponse,
)
from api_gateway.utils.logger import request_id_var, setup_logger
from api_gateway.utils.tokens import estimate_messages_tokens
from api_gateway.presentation.dependencies import get_current_user

router = APIRouter(tags=["Chat"])
logger = setup_logger(__name__, settings.LOG_LEVEL, settings.LOG_FORMAT)


@router.post(
    "/v1/chat/completions",
    summary="聊天补全",
    description="""
OpenAI 兼容的聊天补全接口。

**参数说明**：
- `stream=false`: 返回标准 JSON 响应（可在 Swagger 中直接测试）
- `stream=true`: 返回 SSE 流式响应

**限额**：
- 输入限制：见 `/v1/limits` 的 `max_input_tokens`
- 输出限制：见 `/v1/limits` 的 `max_output_tokens`

**错误码**：
- `413`: 输入过长
- `429`: 请求过于频繁
- `503`: 系统繁忙/队列已满

**SSE 格式**：
```
data: {"id":"...","object":"chat.completion.chunk","created":...,"model":"...","choices":[{"index":0,"delta":{"content":"你"},"finish_reason":null}]}

data: [DONE]
```
    """,
    responses={
        200: {"description": "成功"},
        413: {"model": ErrorResponse, "description": "输入过长"},
        429: {"model": ErrorResponse, "description": "请求过于频繁"},
        503: {"model": ErrorResponse, "description": "系统繁忙"},
    },
)
async def chat_completions(
    request: Request,
    req: ChatCompletionRequest,
    current_user=Depends(get_current_user),
):
    """聊天补全"""
    # 设置请求 ID
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)

    # 记录请求来源用户
    request.state.user_id = current_user.id

    time.time()

    # === Admission：输入长度检查 ===
    input_tokens = estimate_messages_tokens(
        [{"role": m.role, "content": m.content} for m in req.messages]
    )

    if input_tokens > settings.MAX_INPUT_TOKENS:
        logger.warning(
            f"Input too long: {input_tokens} > {settings.MAX_INPUT_TOKENS}",
            extra={
                "input_tokens": input_tokens,
                "max_input_tokens": settings.MAX_INPUT_TOKENS,
            },
        )
        raise HTTPException(
            status_code=413,
            detail={
                "error": {
                    "message": f"Input too long: {input_tokens} tokens, max {settings.MAX_INPUT_TOKENS}",
                    "type": "invalid_request_error",
                    "code": 413,
                }
            },
        )

    # === Admission：输出长度改写 ===
    if req.max_tokens and req.max_tokens > settings.MAX_OUTPUT_TOKENS:
        logger.info(f"max_tokens clamped: {req.max_tokens} -> {settings.MAX_OUTPUT_TOKENS}")
        req.max_tokens = settings.MAX_OUTPUT_TOKENS
    elif not req.max_tokens:
        req.max_tokens = settings.MAX_OUTPUT_TOKENS

    # === Mock 模式 ===
    if settings.USE_MOCK:
        if req.stream:
            return EventSourceResponse(mock_stream_generator(req_id, req.model))
        else:
            return mock_completion_response(req_id, req.model)

    # === 真实模式：转发到 vLLM ===
    if req.stream:
        return EventSourceResponse(
            forward_stream(req_id, req, request), media_type="text/event-stream"
        )
    else:
        return await forward_completion(req_id, req)


# ========================
# Mock 模式生成器
# ========================


async def mock_stream_generator(req_id: str, model: str) -> AsyncGenerator[dict, None]:
    """Mock 流式生成"""
    chunks = ["你", "好", "！", "我", "是", "一", "个", "AI", "助", "手", "。"]

    for _i, chunk in enumerate(chunks):
        await asyncio.sleep(0.1)

        yield {
            "event": "message",
            "data": ChatCompletionChunk(
                id=req_id,
                created=int(time.time()),
                model=model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(content=chunk),
                        finish_reason=None,
                    )
                ],
            ).model_dump_json(),
        }

    # 发送 [DONE]
    yield {"event": "message", "data": "[DONE]"}


def mock_completion_response(req_id: str, model: str) -> ChatCompletionResponse:
    """Mock 非流式响应"""
    return ChatCompletionResponse(
        id=req_id,
        created=int(time.time()),
        model=model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content="你好！我是一个 AI 助手。"),
                finish_reason="stop",
            )
        ],
        usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
    )


# ========================
# 真实转发
# ========================


async def forward_stream(
    req_id: str, req: ChatCompletionRequest, client_request: Request
) -> AsyncGenerator[dict, None]:
    """转发流式请求到 vLLM"""
    upstream_url = f"{settings.UPSTREAM_OPENAI_BASE}/v1/chat/completions"

    payload = {
        "model": req.model,
        "messages": [{"role": m.role, "content": m.content} for m in req.messages],
        "stream": True,
        "max_tokens": req.max_tokens,
        "temperature": req.temperature,
        "top_p": req.top_p,
    }

    try:
        async with (
            httpx.AsyncClient(timeout=settings.TIMEOUT_TOTAL) as client,
            client.stream("POST", upstream_url, json=payload) as response,
        ):
            if response.status_code != 200:
                error_text = await response.aread()
                logger.error(f"Upstream error: {response.status_code} {error_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail={"error": {"message": "Upstream error"}},
                )

            async for line in response.aiter_lines():
                # 检查客户端是否断开
                if await client_request.is_disconnected():
                    logger.info("Client disconnected, cancelling stream")
                    break

                if not line.strip() or not line.startswith("data: "):
                    continue

                data = line[6:]  # 去掉 "data: "
                if data == "[DONE]":
                    yield {"event": "message", "data": "[DONE]"}
                    break

                yield {"event": "message", "data": data}

    except httpx.TimeoutException as exc:
        logger.error("Upstream timeout")
        raise HTTPException(status_code=504, detail={"error": {"message": "Timeout"}}) from exc
    except Exception as exc:
        logger.error(f"Stream error: {exc}")
        raise HTTPException(status_code=500, detail={"error": {"message": str(exc)}}) from exc


async def forward_completion(req_id: str, req: ChatCompletionRequest) -> ChatCompletionResponse:
    """转发非流式请求到 vLLM"""
    upstream_url = f"{settings.UPSTREAM_OPENAI_BASE}/v1/chat/completions"

    payload = {
        "model": req.model,
        "messages": [{"role": m.role, "content": m.content} for m in req.messages],
        "stream": False,
        "max_tokens": req.max_tokens,
        "temperature": req.temperature,
        "top_p": req.top_p,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_TOTAL) as client:
            response = await client.post(upstream_url, json=payload)

        if response.status_code != 200:
            logger.error(f"Upstream error: {response.status_code}")
            raise HTTPException(
                status_code=response.status_code,
                detail={"error": {"message": "Upstream error"}},
            )

        return ChatCompletionResponse(**response.json())

    except httpx.TimeoutException as exc:
        logger.error("Upstream timeout")
        raise HTTPException(status_code=504, detail={"error": {"message": "Timeout"}}) from exc
    except Exception as exc:
        logger.error(f"Completion error: {exc}")
        raise HTTPException(status_code=500, detail={"error": {"message": str(exc)}}) from exc
