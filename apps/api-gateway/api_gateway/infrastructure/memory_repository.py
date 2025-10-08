"""
基础设施层 - 内存仓储实现（用于开发和测试）
"""

from ..domain.entities import ChatSession, Message, User
from ..domain.repositories import IChatSessionRepository, IMessageRepository, IUserRepository


class InMemoryChatSessionRepository(IChatSessionRepository):
    """内存会话仓储"""

    def __init__(self):
        self._storage: dict[str, ChatSession] = {}

    async def get_by_id(self, session_id: str) -> ChatSession | None:
        return self._storage.get(session_id)

    async def get_by_owner(self, owner_id: str) -> list[ChatSession]:
        return [session for session in self._storage.values() if session.owner_id == owner_id]

    async def save(self, session: ChatSession) -> ChatSession:
        self._storage[session.id] = session
        return session

    async def delete(self, session_id: str) -> bool:
        if session_id in self._storage:
            del self._storage[session_id]
            return True
        return False


class InMemoryMessageRepository(IMessageRepository):
    """内存消息仓储"""

    def __init__(self):
        self._storage: dict[str, list[Message]] = {}

    async def get_by_session(self, session_id: str, limit: int = 100) -> list[Message]:
        messages = self._storage.get(session_id, [])
        return messages[-limit:]

    async def save(self, message: Message) -> Message:
        session_messages = self._storage.setdefault(message.session_id, [])
        session_messages.append(message)
        return message


class InMemoryUserRepository(IUserRepository):
    """内存用户仓储"""

    def __init__(self):
        self._storage: dict[str, User] = {}

    async def get_by_id(self, user_id: str) -> User | None:
        return self._storage.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        for user in self._storage.values():
            if user.username == username:
                return user
        return None

    async def save(self, user: User) -> User:
        self._storage[user.id] = user
        return user
