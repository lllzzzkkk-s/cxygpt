"""
数据库配置 - MySQL 优化版本
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from ..config import settings

# 创建基类
Base = declarative_base()

# MySQL 配置（生产级连接池）
if "mysql" in settings.DATABASE_URL.lower():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.LOG_LEVEL == "DEBUG",
        pool_pre_ping=True,  # 连接检活
        pool_size=20,  # 连接池大小
        max_overflow=40,  # 额外连接数
        pool_recycle=3600,  # 连接回收时间（1小时）
        pool_timeout=30,  # 获取连接超时
    )
# SQLite 配置（开发环境）
elif "sqlite" in settings.DATABASE_URL.lower():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.LOG_LEVEL == "DEBUG",
        connect_args={"check_same_thread": False},
    )
# PostgreSQL 配置
else:
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        database_url,
        echo=settings.LOG_LEVEL == "DEBUG",
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=40,
    )

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
