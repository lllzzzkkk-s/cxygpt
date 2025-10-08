"""
表现层 - FastAPI 依赖
"""

from fastapi import Depends

from .container import Container, get_container


def get_chat_completion_use_case(container: Container = Depends(get_container)):
    """获取聊天补全用例"""
    return container.chat_completion_use_case


def get_session_management_use_case(container: Container = Depends(get_container)):
    """获取会话管理用例"""
    return container.session_management_use_case
