"""
测试领域服务
"""

from api_gateway.domain.entities import Message, MessageRole
from api_gateway.domain.services import ChatService


class TestChatService:
    """测试聊天服务"""

    def test_create_message(self):
        """测试创建消息"""
        content = "Hello, world!"
        message = ChatService.create_message("test-session", MessageRole.USER, content)

        assert message.id is not None
        assert message.role == MessageRole.USER
        assert message.content == content
        assert message.tokens > 0

    def test_validate_message_length_valid(self):
        """测试验证消息长度（有效）"""
        short_message = "Hello"
        assert ChatService.validate_message_length(short_message, 100) is True

    def test_validate_message_length_invalid(self):
        """测试验证消息长度（无效）"""
        long_message = "很长的文本" * 1000
        assert ChatService.validate_message_length(long_message, 10) is False

    def test_prepare_context(self, sample_chat_session):
        """测试准备上下文"""
        import uuid

        # 添加历史消息
        for i in range(3):
            msg = Message(
                id=str(uuid.uuid4()),
                session_id=sample_chat_session.id,
                role=MessageRole.USER,
                content=f"Message {i}",
                tokens=5,
            )
            sample_chat_session.add_message(msg)

        # 准备上下文
        context = ChatService.prepare_context(
            session=sample_chat_session,
            new_message_content="New message",
            max_input_tokens=1000,
            system_prompt="You are helpful.",
        )

        # 验证结构
        assert len(context) > 0
        assert context[0]["role"] == "system"
        assert context[0]["content"] == "You are helpful."
        assert context[-1]["role"] == "user"
        assert context[-1]["content"] == "New message"

    def test_prepare_context_without_system_prompt(self, sample_chat_session):
        """测试准备上下文（无系统提示）"""
        context = ChatService.prepare_context(
            session=sample_chat_session,
            new_message_content="Hello",
            max_input_tokens=1000,
            system_prompt="",
        )

        # 第一条不应该是 system
        if len(context) > 0:
            assert context[0]["role"] != "system"

    def test_prepare_context_token_limit(self, sample_chat_session):
        """测试上下文 token 限制"""
        import uuid

        # 添加大量历史消息
        for i in range(100):
            msg = Message(
                id=str(uuid.uuid4()),
                session_id=sample_chat_session.id,
                role=MessageRole.USER,
                content=f"Message {i}" * 10,  # 较长的消息
                tokens=50,
            )
            sample_chat_session.add_message(msg)

        # 准备上下文（限制较小）
        context = ChatService.prepare_context(
            session=sample_chat_session,
            new_message_content="New",
            max_input_tokens=200,  # 较小的限制
            system_prompt="",
        )

        # 应该只包含部分历史消息
        assert len(context) < 100
