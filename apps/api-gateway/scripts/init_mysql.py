#!/usr/bin/env python3
"""
MySQL 数据库初始化脚本

使用方法：
1. 确保 MySQL 服务已启动
2. 根据需要修改 .env 中的数据库连接配置
3. 运行: python scripts/init_mysql.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_gateway.config import settings
from api_gateway.infrastructure.database import Base, init_db


async def create_database():
    """创建数据库（如果不存在）"""
    import aiomysql

    # 解析数据库配置
    db_url = settings.DATABASE_URL
    parts = db_url.split("@")[1].split("/")
    host_port = parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 3306

    user_pass = db_url.split("//")[1].split("@")[0].split(":")
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""

    db_name = parts[1].split("?")[0]

    print(f"🔧 连接 MySQL: {host}:{port}")

    try:
        # 连接到 MySQL（不指定数据库）
        conn = await aiomysql.connect(
            host=host, port=port, user=user, password=password, charset="utf8mb4"
        )

        async with conn.cursor() as cursor:
            # 检查数据库是否存在
            await cursor.execute(
                f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'"
            )
            result = await cursor.fetchone()

            if result:
                print(f"✅ 数据库 '{db_name}' 已存在")
            else:
                # 创建数据库
                await cursor.execute(
                    f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                await conn.commit()
                print(f"✅ 数据库 '{db_name}' 创建成功")

        conn.close()

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n请检查:")
        print("  1. MySQL 服务是否已启动")
        print("  2. 数据库连接配置是否正确")
        print("  3. 用户名密码是否正确")
        sys.exit(1)


async def create_tables():
    """创建所有表"""
    print("\n🔧 开始创建数据库表...")

    try:
        await init_db()
        print("✅ 数据库表创建成功\n")

        # 显示创建的表
        print("📊 已创建的表:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        sys.exit(1)


async def main():
    """主函数"""
    print("=" * 60)
    print("CxyGPT MySQL 数据库初始化")
    print("=" * 60)
    print(f"\n📍 数据库配置: {settings.DATABASE_URL.split('@')[1]}")

    # 创建数据库
    await create_database()

    # 创建表
    await create_tables()

    # 关闭连接
    from api_gateway.infrastructure.database import close_db

    await close_db()

    print("\n" + "=" * 60)
    print("✅ 数据库初始化完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
