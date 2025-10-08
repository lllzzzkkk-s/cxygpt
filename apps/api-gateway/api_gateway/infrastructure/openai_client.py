"""
基础设施层 - OpenAI 兼容客户端实现
"""

import asyncio
from collections.abc import AsyncGenerator

import httpx

from ..config import settings
from ..utils.logger import setup_logger
from .llm_client import ILLMClient

logger = setup_logger(__name__, settings.LOG_LEVEL, settings.LOG_FORMAT)


class OpenAICompatibleClient(ILLMClient):
    """OpenAI 兼容的 LLM 客户端"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.UPSTREAM_OPENAI_BASE

    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> AsyncGenerator[str, None]:
        """流式聊天补全"""
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        async with (
            httpx.AsyncClient(timeout=settings.TIMEOUT_TOTAL) as client,
            client.stream("POST", url, json=payload) as response,
        ):
            if response.status_code != 200:
                error_text = await response.aread()
                logger.error(f"LLM API error: {response.status_code} {error_text}")
                raise Exception(f"LLM API error: {response.status_code}")

            async for line in response.aiter_lines():
                if not line.strip() or not line.startswith("data: "):
                    continue

                data = line[6:]  # 去掉 "data: "
                if data == "[DONE]":
                    break

                try:
                    import json

                    parsed = json.loads(data)
                    content = parsed.get("choices", [{}])[0].get("delta", {}).get("content")
                    if content:
                        yield content
                except Exception as e:
                    logger.warning(f"Failed to parse SSE chunk: {data}, error: {e}")

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """非流式聊天补全"""
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        async with httpx.AsyncClient(timeout=settings.TIMEOUT_TOTAL) as client:
            response = await client.post(url, json=payload)

            if response.status_code != 200:
                logger.error(f"LLM API error: {response.status_code}")
                raise Exception(f"LLM API error: {response.status_code}")

            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")


class MockLLMClient(ILLMClient):
    """Mock LLM 客户端（用于测试）"""

    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> AsyncGenerator[str, None]:
        """Mock 流式响应"""
        chunks = ["你", "好", "！", "我", "是", "一", "个", "AI", "助", "手", "。"]

        for chunk in chunks:
            await asyncio.sleep(0.1)
            yield chunk

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """Mock 非流式响应"""
        return "你好！我是一个 AI 助手。"
