"""
核心模型设计（待实现）

将在后续创建 Django 项目后迁移此模型
"""

# ========================
# chat/models.py（待实现）
# ========================

from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    """部门"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "departments"


class ChatSession(models.Model):
    """会话"""

    id = models.UUIDField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )

    name = models.CharField(max_length=200)
    system_prompt = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_tokens = models.IntegerField(default=0)
    pinned = models.BooleanField(default=False)

    class Meta:
        db_table = "chat_sessions"
        ordering = ["-updated_at"]


class Message(models.Model):
    """消息"""

    ROLE_CHOICES = [
        ("system", "System"),
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    id = models.UUIDField(primary_key=True)
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    # 可选：引用的文档
    # references = models.ManyToManyField('documents.Document', blank=True)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]


class AuditLog(models.Model):
    """审计日志"""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100)

    details = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]


# ========================
# documents/models.py（待实现）
# ========================


class Document(models.Model):
    """文档"""

    id = models.UUIDField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")

    title = models.CharField(max_length=200)
    content = models.TextField()
    file_path = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ACL
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = "documents"


class VectorIndexMeta(models.Model):
    """向量索引元数据"""

    document = models.OneToOneField(
        Document, on_delete=models.CASCADE, related_name="vector_meta"
    )

    index_name = models.CharField(max_length=100)
    embedding_model = models.CharField(max_length=100)
    chunk_size = models.IntegerField()
    chunk_count = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vector_index_meta"
