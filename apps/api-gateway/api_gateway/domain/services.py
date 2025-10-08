"""
领域层 - 领域服务
"""

from ..utils.tokens import estimate_tokens
from .entities import ChatSession, Message, MessageRole


class ChatService:
    """聊天领域服务"""

    @staticmethod
    def prepare_context(
        session: ChatSession,
        new_message_content: str,
        max_input_tokens: int,
        system_prompt: str = "",
    ) -> list[dict[str, str]]:
        """
        准备发送给 LLM 的上下文

        Args:
            session: 会话实体
            new_message_content: 新消息内容
            max_input_tokens: 最大输入 token 数
            system_prompt: 系统提示

        Returns:
            格式化的消息列表
        """
        messages = []

        # 系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 估算当前 token 使用
        current_tokens = estimate_tokens(system_prompt) + estimate_tokens(new_message_content)

        # 从历史消息中选择合适的上下文
        available_tokens = max_input_tokens - current_tokens - 100  # 保留 100 token 余量
        context_messages = session.get_context_messages(available_tokens)

        # 添加历史消息
        for msg in context_messages:
            messages.append({"role": msg.role.value, "content": msg.content})

        # 添加新消息
        messages.append({"role": "user", "content": new_message_content})

        return messages

    @staticmethod
    def create_message(session_id: str, role: MessageRole, content: str) -> Message:
        """创建消息实体"""
        import uuid

        return Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            tokens=estimate_tokens(content),
        )

    @staticmethod
    def validate_message_length(content: str, max_tokens: int) -> bool:
        """验证消息长度"""
        return estimate_tokens(content) <= max_tokens
