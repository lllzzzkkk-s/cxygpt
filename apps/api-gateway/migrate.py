"""
数据库迁移脚本
"""

import asyncio

from sqlalchemy import text

from api_gateway.infrastructure.database import Base, engine
from api_gateway.infrastructure.models import (
    UserModel,
)


async def create_tables():
    """创建所有表"""
    async with engine.begin() as conn:
        # 删除所有表（仅开发环境）
        # await conn.run_sync(Base.metadata.drop_all)

        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    print("✅ 数据库表创建成功")


async def create_default_user():
    """创建默认管理员用户"""
    import uuid

    from passlib.context import CryptContext

    from api_gateway.infrastructure.database import AsyncSessionLocal

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async with AsyncSessionLocal() as session:
        # 检查是否已存在
        result = await session.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        if result.first():
            print("ℹ️  管理员用户已存在")
            return

        # 创建管理员
        admin = UserModel(
            id=uuid.uuid4(),
            username="admin",
            email="admin@cxygpt.local",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)
        await session.commit()

    print("✅ 默认管理员用户创建成功")
    print("   用户名: admin")
    print("   密码: admin123")
    print("   ⚠️  请在生产环境修改密码！")


async def main():
    """主函数"""
    print("开始数据库迁移...")
    try:
        await create_tables()
        await create_default_user()
        print("\n✅ 数据库迁移完成！")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
