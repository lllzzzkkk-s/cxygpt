"""
测试 SQLAlchemy 仓储
"""

import pytest

from api_gateway.infrastructure.sqlalchemy_repository import (
    SQLAlchemyChatSessionRepository,
    SQLAlchemyUserRepository,
)


@pytest.mark.db
class TestSQLAlchemyChatSessionRepository:
    """测试会话仓储"""

    @pytest.mark.asyncio
    async def test_save_and_get_session(self, db_session, sample_chat_session):
        """测试保存和获取会话"""
        repo = SQLAlchemyChatSessionRepository(db_session)

        # 保存
        saved = await repo.save(sample_chat_session)
        assert saved.id == sample_chat_session.id

        # 获取
        retrieved = await repo.get_by_id(sample_chat_session.id)
        assert retrieved is not None
        assert retrieved.id == sample_chat_session.id
        assert retrieved.name == sample_chat_session.name

    @pytest.mark.asyncio
    async def test_get_by_owner(self, db_session, sample_user, sample_chat_session):
        """测试按用户获取会话"""
        import uuid

        repo = SQLAlchemyChatSessionRepository(db_session)

        # 保存多个会话
        await repo.save(sample_chat_session)

        # 创建第二个会话
        from datetime import datetime

        from api_gateway.domain.entities import ChatSession

        session2 = ChatSession(
            id=str(uuid.uuid4()),
            owner_id=sample_user.id,
            name="Session 2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await repo.save(session2)

        # 获取用户的所有会话
        sessions = await repo.get_by_owner(sample_user.id)
        assert len(sessions) == 2

    @pytest.mark.asyncio
    async def test_delete_session(self, db_session, sample_chat_session):
        """测试删除会话"""
        repo = SQLAlchemyChatSessionRepository(db_session)

        # 保存
        await repo.save(sample_chat_session)

        # 删除
        result = await repo.delete(sample_chat_session.id)
        assert result is True

        # 验证已删除
        retrieved = await repo.get_by_id(sample_chat_session.id)
        assert retrieved is None


@pytest.mark.db
class TestSQLAlchemyUserRepository:
    """测试用户仓储"""

    @pytest.mark.asyncio
    async def test_save_and_get_user(self, db_session, sample_user):
        """测试保存和获取用户"""
        repo = SQLAlchemyUserRepository(db_session)

        # 保存
        saved = await repo.save(sample_user)
        assert saved.id == sample_user.id

        # 按 ID 获取
        retrieved = await repo.get_by_id(sample_user.id)
        assert retrieved is not None
        assert retrieved.username == sample_user.username

    @pytest.mark.asyncio
    async def test_get_by_username(self, db_session, sample_user):
        """测试按用户名获取用户"""
        repo = SQLAlchemyUserRepository(db_session)

        # 保存
        await repo.save(sample_user)

        # 按用户名获取
        retrieved = await repo.get_by_username(sample_user.username)
        assert retrieved is not None
        assert retrieved.id == sample_user.id
