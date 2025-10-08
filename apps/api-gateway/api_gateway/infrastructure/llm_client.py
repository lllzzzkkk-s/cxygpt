"""
基础设施层 - LLM 客户端接口
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class ILLMClient(ABC):
    """LLM 客户端接口"""

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天补全

        Args:
            messages: 消息列表
            model: 模型名称
            max_tokens: 最大 token 数
            temperature: 温度
            top_p: Top-P

        Yields:
            生成的文本块
        """
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        非流式聊天补全

        Returns:
            完整的生成文本
        """
        pass
