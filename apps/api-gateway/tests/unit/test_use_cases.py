"""
测试用例
"""

from unittest.mock import AsyncMock

import pytest

from api_gateway.application.use_cases import ChatCompletionUseCase
from api_gateway.domain.services import ChatService


class TestChatCompletionUseCase:
    """测试聊天补全用例"""

    @pytest.mark.asyncio
    async def test_execute_creates_messages(self, sample_chat_session):
        """测试执行用例创建消息"""
        # Mock 仓储
        session_repo = AsyncMock()
        message_repo = AsyncMock()
        session_repo.get_by_id.return_value = sample_chat_session
        session_repo.save.return_value = sample_chat_session

        # Mock LLM 客户端
        llm_client = AsyncMock()

        async def mock_stream(*args, **kwargs):
            """Mock 流式生成"""
            for chunk in ["Hello", " ", "World"]:
                yield chunk

        llm_client.chat_completion_stream = mock_stream

        # 创建用例
        use_case = ChatCompletionUseCase(
            session_repo=session_repo,
            message_repo=message_repo,
            llm_client=llm_client,
            chat_service=ChatService(),
        )

        # 执行
        result = []
        async for chunk in use_case.execute(
            session_id=sample_chat_session.id, user_message="Test message", stream=True
        ):
            result.append(chunk)

        # 验证
        assert "".join(result) == "Hello World"
        assert message_repo.save.call_count == 2  # user + assistant

    @pytest.mark.asyncio
    async def test_execute_validates_message_length(self, sample_chat_session):
        """测试用例验证消息长度"""
        session_repo = AsyncMock()
        message_repo = AsyncMock()
        llm_client = AsyncMock()

        session_repo.get_by_id.return_value = sample_chat_session

        use_case = ChatCompletionUseCase(
            session_repo=session_repo,
            message_repo=message_repo,
            llm_client=llm_client,
            chat_service=ChatService(),
        )

        # 尝试发送超长消息
        long_message = "很长的文本" * 10000

        with pytest.raises(ValueError, match="too long"):
            async for _ in use_case.execute(
                session_id=sample_chat_session.id, user_message=long_message
            ):
                pass

    @pytest.mark.asyncio
    async def test_execute_session_not_found(self):
        """测试会话不存在"""
        session_repo = AsyncMock()
        message_repo = AsyncMock()
        llm_client = AsyncMock()

        session_repo.get_by_id.return_value = None

        use_case = ChatCompletionUseCase(
            session_repo=session_repo,
            message_repo=message_repo,
            llm_client=llm_client,
            chat_service=ChatService(),
        )

        with pytest.raises(ValueError, match="not found"):
            async for _ in use_case.execute(session_id="non-existent-id", user_message="Test"):
                pass
