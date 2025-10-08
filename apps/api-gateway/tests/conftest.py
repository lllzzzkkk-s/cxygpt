"""
测试配置和 fixtures
"""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api_gateway.domain.entities import ChatSession, Message, MessageRole, User
from api_gateway.infrastructure.database import Base

# 创建 Faker 实例
fake = Faker()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_user() -> User:
    """创建示例用户实体"""
    import uuid
    from datetime import datetime

    return User(
        id=str(uuid.uuid4()),
        username=fake.user_name(),
        email=fake.email(),
        hashed_password="$2b$12$3kKpZ.dummyHashValueForTests7rjD1S8C8L0/LO",
        is_active=True,
        is_superuser=False,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_message() -> Message:
    """创建示例消息实体"""
    import uuid
    from datetime import datetime

    return Message(
        id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        role=MessageRole.USER,
        content="Hello, AI!",
        tokens=10,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_chat_session(sample_user) -> ChatSession:
    """创建示例会话实体"""
    import uuid
    from datetime import datetime

    return ChatSession(
        id=str(uuid.uuid4()),
        owner_id=sample_user.id,
        name="Test Session",
        messages=[],
        system_prompt="You are a helpful assistant.",
        total_tokens=0,
        pinned=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
