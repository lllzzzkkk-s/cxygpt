"""
Pydantic 模型
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, ConfigDict


class ChatMessage(BaseModel):
    """聊天消息"""

    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    """聊天补全请求"""

    model: str
    messages: list[ChatMessage]
    stream: bool = False
    max_tokens: int | None = None
    temperature: float | None = 0.7
    top_p: float | None = 0.9
    stop: list[str] | None = None
    n: int | None = 1
    presence_penalty: float | None = 0.0
    frequency_penalty: float | None = 0.0
    user: str | None = None


class ChatCompletionChoice(BaseModel):
    """聊天补全选项"""

    index: int
    message: ChatMessage
    finish_reason: str | None = None


class ChatCompletionResponse(BaseModel):
    """聊天补全响应"""

    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: dict[str, int] | None = None


class ChatCompletionChunkDelta(BaseModel):
    """流式响应增量"""

    role: str | None = None
    content: str | None = None


class ChatCompletionChunkChoice(BaseModel):
    """流式响应选项"""

    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: str | None = None


class ChatCompletionChunk(BaseModel):
    """流式响应"""

    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatCompletionChunkChoice]


class LimitsResponse(BaseModel):
    """限额响应"""

    max_input_tokens: int
    max_output_tokens: int
    rate_qps: int
    rate_tpm: int
    queue_size: int
    single_user: bool
    profile: str


class HealthResponse(BaseModel):
    """健康检查响应"""

    ok: bool = True


class ErrorResponse(BaseModel):
    """错误响应"""

    error: dict[str, Any] = Field(
        ...,
        examples=[
            {
                "message": "Input too long",
                "type": "invalid_request_error",
                "code": 413,
            }
        ],
    )


class Token(BaseModel):
    """访问令牌响应"""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """登录请求体"""

    username: str
    password: str


class UserProfile(BaseModel):
    """用户信息"""

    id: str
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(Token):
    """登录响应"""

    user: UserProfile


class KnowledgeDocument(BaseModel):
    """知识库文档信息"""

    id: str
    filename: str
    display_name: str | None = None
    size_bytes: int
    status: Literal["uploaded", "embedding", "ready", "error"]
    chunk_count: int | None = None
    embedding_model: str | None = None
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeUploadResponse(BaseModel):
    """上传文档响应"""

    document: KnowledgeDocument


class KnowledgeEmbeddingRequest(BaseModel):
    """触发向量化请求"""

    embedding_model: str | None = None
