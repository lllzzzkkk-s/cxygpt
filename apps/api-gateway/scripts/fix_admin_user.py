#!/usr/bin/env python3
"""
Fix admin user in database
"""

import asyncio
import uuid
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from api_gateway.config import settings
from api_gateway.infrastructure.models import UserModel


async def fix_admin_user():
    """Fix or create admin user with proper UUID format"""
    
    # Create engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
    )
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # First, try to find the admin user
            stmt = select(UserModel).where(UserModel.username == "admin")
            result = await session.execute(stmt)
            admin_user = result.scalar_one_or_none()
            
            if admin_user:
                print(f"Admin user already exists with ID: {admin_user.id}")
                # Update password hash to ensure it's correct
                admin_user.hashed_password = "$2b$12$dIsQkhimp6QgZNHJseTkC.lGaLPaxK5Vj34KRrV.kY20/YYId87gW"
                await session.commit()
                print("Admin user password updated")
            else:
                # Create new admin user
                admin_id = str(uuid.uuid4())
                new_admin = UserModel(
                    id=admin_id,
                    username="admin",
                    email="admin@cxygpt.local",
                    hashed_password="$2b$12$dIsQkhimp6QgZNHJseTkC.lGaLPaxK5Vj34KRrV.kY20/YYId87gW",
                    is_active=True,
                    is_superuser=True,
                )
                session.add(new_admin)
                await session.commit()
                print(f"Admin user created with ID: {admin_id}")
                
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_admin_user())