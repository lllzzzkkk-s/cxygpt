"""
测试领域实体
"""

from datetime import datetime

from api_gateway.domain.entities import Message, MessageRole


class TestMessage:
    """测试消息实体"""

    def test_create_message(self, sample_message):
        """测试创建消息"""
        assert sample_message.id is not None
        assert sample_message.role == MessageRole.USER
        assert sample_message.content == "Hello, AI!"
        assert sample_message.tokens == 10
        assert isinstance(sample_message.created_at, datetime)

    def test_message_role_enum(self):
        """测试消息角色枚举"""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"


class TestChatSession:
    """测试会话实体"""

    def test_create_session(self, sample_chat_session):
        """测试创建会话"""
        assert sample_chat_session.id is not None
        assert sample_chat_session.name == "Test Session"
        assert len(sample_chat_session.messages) == 0
        assert sample_chat_session.total_tokens == 0
        assert sample_chat_session.pinned is False

    def test_add_message(self, sample_chat_session, sample_message):
        """测试添加消息"""
        initial_count = len(sample_chat_session.messages)
        initial_tokens = sample_chat_session.total_tokens

        sample_chat_session.add_message(sample_message)

        assert len(sample_chat_session.messages) == initial_count + 1
        assert sample_chat_session.total_tokens == initial_tokens + sample_message.tokens
        assert sample_chat_session.messages[-1] == sample_message

    def test_get_context_messages_no_limit(self, sample_chat_session):
        """测试获取上下文消息（无限制）"""
        import uuid

        # 添加多条消息
        for i in range(5):
            msg = Message(
                id=str(uuid.uuid4()),
                session_id=sample_chat_session.id,
                role=MessageRole.USER,
                content=f"Message {i}",
                tokens=10,
            )
            sample_chat_session.add_message(msg)

        context = sample_chat_session.get_context_messages()
        assert len(context) == 5

    def test_get_context_messages_with_limit(self, sample_chat_session):
        """测试获取上下文消息（带限制）"""
        import uuid

        # 添加多条消息，每条 10 tokens
        for i in range(5):
            msg = Message(
                id=str(uuid.uuid4()),
                session_id=sample_chat_session.id,
                role=MessageRole.USER,
                content=f"Message {i}",
                tokens=10,
            )
            sample_chat_session.add_message(msg)

        # 限制为 25 tokens，应该返回最后 2 条消息
        context = sample_chat_session.get_context_messages(max_tokens=25)
        assert len(context) == 2
        assert context[0].content == "Message 3"
        assert context[1].content == "Message 4"


class TestUser:
    """测试用户实体"""

    def test_create_user(self, sample_user):
        """测试创建用户"""
        assert sample_user.id is not None
        assert sample_user.username is not None
        assert sample_user.email is not None
        assert sample_user.is_active is True
        assert sample_user.is_superuser is False
