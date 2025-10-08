"""
领域层 - 仓储接口
"""

from abc import ABC, abstractmethod

from .entities import ChatSession, Message, User


class IChatSessionRepository(ABC):
    """会话仓储接口"""

    @abstractmethod
    async def get_by_id(self, session_id: str) -> ChatSession | None:
        """根据 ID 获取会话"""
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: str) -> list[ChatSession]:
        """获取用户的所有会话"""
        pass

    @abstractmethod
    async def save(self, session: ChatSession) -> ChatSession:
        """保存会话"""
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """删除会话"""
        pass


class IMessageRepository(ABC):
    """消息仓储接口"""

    @abstractmethod
    async def get_by_session(self, session_id: str, limit: int = 100) -> list[Message]:
        """获取会话的消息"""
        pass

    @abstractmethod
    async def save(self, message: Message) -> Message:
        """保存消息"""
        pass


class IUserRepository(ABC):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        """根据 ID 获取用户"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """保存用户"""
        pass
