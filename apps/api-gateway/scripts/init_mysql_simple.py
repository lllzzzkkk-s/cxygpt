#!/usr/bin/env python3
"""MySQL Database Initialization Script"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api_gateway.config import settings
from api_gateway.infrastructure.database import Base, init_db


async def create_database():
    """Create database if not exists"""
    import aiomysql

    # Parse database config
    db_url = settings.DATABASE_URL
    parts = db_url.split("@")[1].split("/")
    host_port = parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 3306

    user_pass = db_url.split("//")[1].split("@")[0].split(":")
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""

    db_name = parts[1].split("?")[0]

    print(f"Connecting to MySQL: {host}:{port}")

    try:
        conn = await aiomysql.connect(
            host=host, port=port, user=user, password=password, charset="utf8mb4"
        )

        async with conn.cursor() as cursor:
            await cursor.execute(
                f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'"
            )
            result = await cursor.fetchone()

            if result:
                print(f"Database '{db_name}' already exists")
            else:
                await cursor.execute(
                    f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                await conn.commit()
                print(f"Database '{db_name}' created successfully")

        conn.close()

    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nPlease check:")
        print("  1. MySQL service is running")
        print("  2. Database connection config is correct")
        print("  3. Username and password are correct")
        sys.exit(1)


async def create_tables():
    """Create all tables"""
    print("\nCreating database tables...")

    try:
        await init_db()
        print("Database tables created successfully\n")

        print("Created tables:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

    except Exception as e:
        print(f"Failed to create tables: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


async def main():
    """Main function"""
    print("=" * 60)
    print("CxyGPT MySQL Database Initialization")
    print("=" * 60)
    print(f"\nDatabase: {settings.DATABASE_URL.split('@')[1]}\n")

    # Create database
    await create_database()

    # Create tables
    await create_tables()

    # Close connection
    from api_gateway.infrastructure.database import close_db

    await close_db()

    print("\n" + "=" * 60)
    print("Database initialization completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
