# CxyGPT Django Admin

Django 管理后台，提供用户、会话、消息、文档等元数据管理。

## 初始化项目（后续）

```bash
cd services/admin
.\venv\Scripts\Activate.ps1

# 创建 Django 项目
django-admin startproject cxyadmin .

# 创建 app
python manage.py startapp chat
python manage.py startapp documents

# 迁移数据库
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 运行
python manage.py runserver 8002
```

## 核心模型（待实现）

### chat/models.py

- `User`: 用户（扩展 Django User）
- `Department`: 部门
- `ChatSession`: 会话
- `Message`: 消息
- `AuditLog`: 审计日志

### documents/models.py

- `Document`: 文档
- `VectorIndexMeta`: 向量索引元数据

## DRF 只读 API（待实现）

- `GET /api/sessions`: 会话列表
- `GET /api/messages?session_id=xxx`: 消息历史

## 当前状态

**⚠️ 雏形阶段**：项目结构已规划，核心模型设计已完成，待后续实现。

建议优先完成前端 + 网关的集成测试，Django 作为数据持久化层可后续接入。
