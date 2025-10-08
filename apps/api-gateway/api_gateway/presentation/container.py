"""
表现层 - 依赖注入容器（更新版）
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import ChatCompletionUseCase, SessionManagementUseCase
from ..config import settings
from ..domain.services import ChatService
from ..infrastructure.database import get_db
from ..infrastructure.memory_repository import (
    InMemoryChatSessionRepository,
    InMemoryMessageRepository,
    InMemoryUserRepository,
)
from ..infrastructure.openai_client import MockLLMClient, OpenAICompatibleClient
from ..infrastructure.sqlalchemy_repository import (
    SQLAlchemyChatSessionRepository,
    SQLAlchemyMessageRepository,
    SQLAlchemyUserRepository,
)


class Container:
    """依赖注入容器"""

    def __init__(self, db_session: AsyncSession = None):
        # 根据配置选择仓储实现
        db_url = settings.DATABASE_URL.lower()
        use_database = any(proto in db_url for proto in ("mysql", "postgresql", "sqlite"))

        if use_database and db_session:
            # 使用数据库仓储
            self.session_repo = SQLAlchemyChatSessionRepository(db_session)
            self.message_repo = SQLAlchemyMessageRepository(db_session)
            self.user_repo = SQLAlchemyUserRepository(db_session)
        else:
            # 使用内存仓储（开发/测试）
            self.session_repo = InMemoryChatSessionRepository()
            self.message_repo = InMemoryMessageRepository()
            self.user_repo = InMemoryUserRepository()

        # LLM 客户端
        if settings.USE_MOCK:
            self.llm_client = MockLLMClient()
        else:
            self.llm_client = OpenAICompatibleClient(settings.UPSTREAM_OPENAI_BASE)

        # 领域服务
        self.chat_service = ChatService()

        # 用例
        self.chat_completion_use_case = ChatCompletionUseCase(
            session_repo=self.session_repo,
            message_repo=self.message_repo,
            llm_client=self.llm_client,
            chat_service=self.chat_service,
        )

        self.session_management_use_case = SessionManagementUseCase(
            session_repo=self.session_repo, message_repo=self.message_repo
        )


async def get_container(db: AsyncSession = Depends(get_db)) -> Container:
    """获取容器实例"""
    return Container(db_session=db)
