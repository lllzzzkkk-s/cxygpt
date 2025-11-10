"""
SQLAlchemy ORM 模型 - MySQL 优化版本
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import BINARY, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON, TypeDecorator

from .database import Base


class UUIDBinary(TypeDecorator):
    """使用 BINARY(16) 存储 UUID，MySQL 最优方案"""

    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """存储时：将 UUID 字符串转为 bytes"""
        if value is None:
            return value
        if isinstance(value, str):
            return uuid.UUID(value).bytes
        if isinstance(value, uuid.UUID):
            return value.bytes
        return value

    def process_result_value(self, value, dialect):
        """读取时：将 bytes 转为 UUID 字符串"""
        if value is None:
            return value
        return str(uuid.UUID(bytes=value))


class MessageRoleEnum(str, enum.Enum):
    """消息角色枚举"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class UserModel(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(UUIDBinary, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    sessions = relationship(
        "ChatSessionModel", back_populates="owner", cascade="all, delete-orphan"
    )
    documents = relationship("DocumentModel", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLogModel", back_populates="user")


class DepartmentModel(Base):
    """部门表"""

    __tablename__ = "departments"

    id = Column(UUIDBinary, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    sessions = relationship("ChatSessionModel", back_populates="department")
    documents = relationship("DocumentModel", back_populates="department")


class ChatSessionModel(Base):
    """会话表"""

    __tablename__ = "chat_sessions"

    id = Column(UUIDBinary, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id = Column(UUIDBinary, ForeignKey("departments.id", ondelete="SET NULL"))
    name = Column(String(200), nullable=False)
    system_prompt = Column(Text, default="")
    total_tokens = Column(Integer, default=0)
    pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True
    )

    # 关系
    owner = relationship("UserModel", back_populates="sessions")
    department = relationship("DepartmentModel", back_populates="sessions")
    messages = relationship(
        "MessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="MessageModel.created_at",
    )


class MessageModel(Base):
    """消息表"""

    __tablename__ = "messages"

    id = Column(UUIDBinary, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        UUIDBinary,
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(SQLEnum(MessageRoleEnum), nullable=False)
    content = Column(Text, nullable=False)
    tokens = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    session = relationship("ChatSessionModel", back_populates="messages")


class DocumentModel(Base):
    """文档表"""

    __tablename__ = "documents"

    id = Column(UUIDBinary, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    department_id = Column(UUIDBinary, ForeignKey("departments.id", ondelete="SET NULL"))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(500))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    owner = relationship("UserModel", back_populates="documents")
    department = relationship("DepartmentModel", back_populates="documents")
    vector_meta = relationship(
        "VectorIndexMetaModel",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
    )


class KnowledgeDocumentStatus(str, enum.Enum):
    """知识库文档状态"""

    UPLOADED = "uploaded"
    EMBEDDING = "embedding"
    READY = "ready"
    ERROR = "error"


class KnowledgeDocumentModel(Base):
    """知识库文档"""

    __tablename__ = "knowledge_documents"

    id = Column(UUIDBinary, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    display_name = Column(String(255))
    size_bytes = Column(Integer, nullable=False)
    status = Column(
        SQLEnum(KnowledgeDocumentStatus),
        nullable=False,
        default=KnowledgeDocumentStatus.UPLOADED,
    )
    chunk_count = Column(Integer)
    embedding_model = Column(String(100))
    storage_path = Column(String(500), nullable=False)
    error_message = Column(Text)
    metadata_json = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("UserModel", backref="knowledge_documents")


class VectorIndexMetaModel(Base):
    """向量索引元数据表"""

    __tablename__ = "vector_index_meta"

    id = Column(UUIDBinary, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(
        UUIDBinary,
        ForeignKey("documents.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    index_name = Column(String(100), nullable=False)
    embedding_model = Column(String(100), nullable=False)
    chunk_size = Column(Integer, nullable=False)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    document = relationship("DocumentModel", back_populates="vector_meta")


class AuditLogModel(Base):
    """审计日志表"""

    __tablename__ = "audit_logs"

    id = Column(UUIDBinary, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUIDBinary, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=False)
    resource_id = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    user = relationship("UserModel", back_populates="audit_logs")
