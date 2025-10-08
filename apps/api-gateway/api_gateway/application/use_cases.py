"""
应用层 - 用例实现
"""

from collections.abc import AsyncGenerator

from ..config import settings
from ..domain.entities import ChatSession, MessageRole
from ..domain.repositories import IChatSessionRepository, IMessageRepository
from ..domain.services import ChatService
from ..infrastructure.llm_client import ILLMClient


class ChatCompletionUseCase:
    """聊天补全用例"""

    def __init__(
        self,
        session_repo: IChatSessionRepository,
        message_repo: IMessageRepository,
        llm_client: ILLMClient,
        chat_service: ChatService,
    ):
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.llm_client = llm_client
        self.chat_service = chat_service

    async def execute(
        self,
        session_id: str,
        user_message: str,
        stream: bool = False,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> AsyncGenerator[str, None]:
        """
        执行聊天补全

        Args:
            session_id: 会话 ID
            user_message: 用户消息
            stream: 是否流式返回
            max_tokens: 最大输出 token 数
            temperature: 温度
            top_p: Top-P

        Yields:
            生成的文本块
        """
        # 1. 获取会话
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # 2. 验证消息长度
        if not self.chat_service.validate_message_length(user_message, settings.MAX_INPUT_TOKENS):
            raise ValueError(f"Message too long. Max {settings.MAX_INPUT_TOKENS} tokens")

        # 3. 创建用户消息
        user_msg = self.chat_service.create_message(session.id, MessageRole.USER, user_message)

        # 4. 保存用户消息
        await self.message_repo.save(user_msg)
        session.add_message(user_msg)

        # 5. 准备上下文
        context = self.chat_service.prepare_context(
            session=session,
            new_message_content=user_message,
            max_input_tokens=settings.MAX_INPUT_TOKENS,
            system_prompt=session.system_prompt,
        )

        # 6. 调用 LLM
        full_response = ""
        async for chunk in self.llm_client.chat_completion_stream(
            messages=context,
            model=settings.DEFAULT_MODEL,
            max_tokens=max_tokens or settings.MAX_OUTPUT_TOKENS,
            temperature=temperature,
            top_p=top_p,
        ):
            full_response += chunk
            yield chunk

        # 7. 创建助手消息
        assistant_msg = self.chat_service.create_message(
            session.id, MessageRole.ASSISTANT, full_response
        )

        # 8. 保存助手消息
        await self.message_repo.save(assistant_msg)
        session.add_message(assistant_msg)

        # 9. 更新会话
        await self.session_repo.save(session)


class SessionManagementUseCase:
    """会话管理用例"""

    def __init__(self, session_repo: IChatSessionRepository, message_repo: IMessageRepository):
        self.session_repo = session_repo
        self.message_repo = message_repo

    async def create_session(
        self, owner_id: str, name: str, system_prompt: str = ""
    ) -> ChatSession:
        """创建新会话"""
        import uuid

        session = ChatSession(
            id=str(uuid.uuid4()), owner_id=owner_id, name=name, system_prompt=system_prompt
        )

        return await self.session_repo.save(session)

    async def get_user_sessions(self, owner_id: str) -> list[ChatSession]:
        """获取用户的所有会话"""
        return await self.session_repo.get_by_owner(owner_id)

    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        return await self.session_repo.delete(session_id)
