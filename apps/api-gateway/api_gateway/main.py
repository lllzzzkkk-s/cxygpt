"""
CxyGPT API Gateway

FastAPI 网关，提供 OpenAI 兼容 API
"""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api_gateway.config import get_profile_name, settings
from api_gateway.routes import auth, chat, knowledge, system
from api_gateway.utils.logger import request_id_var, setup_logger

# 设置日志
logger = setup_logger(__name__, settings.LOG_LEVEL, settings.LOG_FORMAT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    logger.info(
        "Starting CxyGPT API Gateway",
        extra={
            "mode": "SINGLE_USER" if settings.SINGLE_USER else "MULTI_USER",
            "profile": get_profile_name(settings),
            "use_mock": settings.USE_MOCK,
            "max_input_tokens": settings.MAX_INPUT_TOKENS,
            "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
        },
    )
    yield
    logger.info("Shutting down CxyGPT API Gateway")


# 创建应用
app = FastAPI(
    title="CxyGPT API Gateway",
    version="0.1.0",
    description="""
## CxyGPT API Gateway

OpenAI 兼容的本地大模型 API 网关。

### 功能特性

- ✅ OpenAI 兼容 API (`/v1/chat/completions`)
- ✅ SSE 流式渲染
- ✅ Admission（请求整形）
- ✅ 单人/多人双模式
- ✅ 显存自适应分档
- ✅ Mock 模式（开发测试）

### 快速开始

1. **健康检查**：`GET /healthz`
2. **获取限额**：`GET /v1/limits`
3. **聊天补全**：`POST /v1/chat/completions`

### 错误码

- `413`: 输入过长（超过 `max_input_tokens`）
- `429`: 请求过于频繁（超过 QPS 或 TPM 限制）
- `503`: 系统繁忙或队列已满

### 当前配置

- **模式**: {mode}
- **档位**: {profile}
- **Mock**: {use_mock}
- **输入限制**: {max_in} tokens
- **输出限制**: {max_out} tokens
    """.format(
        mode="单人模式" if settings.SINGLE_USER else "多人模式",
        profile=get_profile_name(settings),
        use_mock="启用" if settings.USE_MOCK else "禁用",
        max_in=settings.MAX_INPUT_TOKENS,
        max_out=settings.MAX_OUTPUT_TOKENS,
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
# 生产环境应限制来源
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# 请求 ID 中间件
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """为每个请求添加唯一 ID"""
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response


# 注册路由
app.include_router(system.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(knowledge.router)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"message": "Internal server error", "type": "server_error"}},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_gateway.main:app",
        host=settings.GATEWAY_HOST,
        port=settings.GATEWAY_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
