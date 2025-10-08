"""
SQLAlchemy 数据库仓储实现
"""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..domain.entities import ChatSession, Message, MessageRole, User
from ..domain.repositories import IChatSessionRepository, IMessageRepository, IUserRepository
from .models import ChatSessionModel, MessageModel, MessageRoleEnum, UserModel


class SQLAlchemyChatSessionRepository(IChatSessionRepository):
    """SQLAlchemy 会话仓储"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, session_id: str) -> ChatSession | None:
        """根据 ID 获取会话"""
        stmt = (
            select(ChatSessionModel)
            .options(selectinload(ChatSessionModel.messages))
            .where(ChatSessionModel.id == session_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def get_by_owner(self, owner_id: str) -> list[ChatSession]:
        """获取用户的所有会话"""
        from sqlalchemy.orm import selectinload

        stmt = (
            select(ChatSessionModel)
            .where(ChatSessionModel.owner_id == owner_id)
            .options(selectinload(ChatSessionModel.messages))  # 预加载消息
            .order_by(ChatSessionModel.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def save(self, session: ChatSession) -> ChatSession:
        """保存会话"""
        # 查找是否存在
        stmt = select(ChatSessionModel).where(ChatSessionModel.id == session.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # 更新
            existing.name = session.name
            existing.system_prompt = session.system_prompt
            existing.total_tokens = session.total_tokens
            existing.pinned = session.pinned
            existing.updated_at = session.updated_at
        else:
            # 新建
            model = ChatSessionModel(
                id=session.id,
                owner_id=session.owner_id,
                name=session.name,
                system_prompt=session.system_prompt,
                total_tokens=session.total_tokens,
                pinned=session.pinned,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
            self.session.add(model)

        await self.session.commit()
        return session

    async def delete(self, session_id: str) -> bool:
        """删除会话"""
        stmt = delete(ChatSessionModel).where(ChatSessionModel.id == session_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    @staticmethod
    def _to_entity(model: ChatSessionModel) -> ChatSession:
        """ORM 模型转实体"""
        messages = [
            Message(
                id=str(m.id),
                session_id=str(m.session_id),
                role=MessageRole(m.role.value),
                content=m.content,
                tokens=m.tokens,
                created_at=m.created_at,
            )
            for m in model.messages
        ]

        return ChatSession(
            id=str(model.id),
            owner_id=str(model.owner_id) if model.owner_id else None,
            name=model.name,
            messages=messages,
            system_prompt=model.system_prompt,
            total_tokens=model.total_tokens,
            pinned=model.pinned,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyMessageRepository(IMessageRepository):
    """SQLAlchemy 消息仓储"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_session(self, session_id: str, limit: int = 100) -> list[Message]:
        """获取会话的消息"""
        stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in reversed(models)]

    async def save(self, message: Message) -> Message:
        """保存消息"""
        model = MessageModel(
            id=message.id,
            session_id=message.session_id,
            role=MessageRoleEnum(message.role.value),
            content=message.content,
            tokens=message.tokens,
            created_at=message.created_at,
        )
        self.session.add(model)
        await self.session.commit()
        return message

    @staticmethod
    def _to_entity(model: MessageModel) -> Message:
        """ORM 模型转实体"""
        return Message(
            id=str(model.id),
            session_id=str(model.session_id),
            role=MessageRole(model.role.value),
            content=model.content,
            tokens=model.tokens,
            created_at=model.created_at,
        )


class SQLAlchemyUserRepository(IUserRepository):
    """SQLAlchemy 用户仓储"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        """根据 ID 获取用户"""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def save(self, user: User) -> User:
        """保存用户"""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # 更新
            existing.username = user.username
            existing.email = user.email
            existing.hashed_password = user.hashed_password
            existing.is_active = user.is_active
            existing.is_superuser = user.is_superuser
        else:
            # 新建
            model = UserModel(
                id=user.id,
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
            )
            self.session.add(model)

        await self.session.commit()
        return user

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        """ORM 模型转实体"""
        return User(
            id=str(model.id),
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
        )
