"""
领域层 - 实体定义
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """消息角色"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """消息实体"""

    id: str
    session_id: str
    role: MessageRole
    content: str
    tokens: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if isinstance(self.role, str):
            self.role = MessageRole(self.role)


@dataclass
class ChatSession:
    """会话实体"""

    id: str
    owner_id: str | None
    name: str
    messages: list[Message] = field(default_factory=list)
    system_prompt: str = ""
    total_tokens: int = 0
    pinned: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, message: Message):
        """添加消息"""
        if message.session_id != self.id:
            message.session_id = self.id
        self.messages.append(message)
        self.total_tokens += message.tokens
        self.updated_at = datetime.utcnow()

    def get_context_messages(self, max_tokens: int | None = None) -> list[Message]:
        """获取上下文消息（带 token 限制）"""
        if not max_tokens:
            return self.messages

        # 从后向前累加，直到超过 token 限制
        selected = []
        total = 0
        for msg in reversed(self.messages):
            if total + msg.tokens > max_tokens:
                break
            selected.insert(0, msg)
            total += msg.tokens

        return selected


@dataclass
class User:
    """用户实体"""

    id: str
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
