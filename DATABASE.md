# ================================
# 数据库使用文档
# ================================

## 初始化数据库

### 方法 1：使用迁移脚本（推荐开发环境）

```bash
cd apps/api-gateway

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 运行迁移脚本
python migrate.py
```

**输出**：
```
开始数据库迁移...
✅ 数据库表创建成功
✅ 默认管理员用户创建成功
   用户名: admin
   密码: admin123
   ⚠️  请在生产环境修改密码！

✅ 数据库迁移完成！
```

---

### 方法 2：使用 Alembic（推荐生产环境）

```bash
cd apps/api-gateway

# 初始化 Alembic（仅第一次）
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

---

## 数据库配置

### MySQL（默认）

在 `.env` 文件中设置：
```env
DATABASE_URL=mysql+aiomysql://cxygpt:cxygpt123@localhost:3306/cxygpt?charset=utf8mb4
```

### SQLite（可选，本地快速验证）

```env
DATABASE_URL=sqlite+aiosqlite:///./cxygpt.db
```

### Docker Compose（推荐）

```bash
# 启动 MySQL
docker-compose -f docker-compose.dev.yml up -d mysql

# 等待数据库就绪
docker-compose -f docker-compose.dev.yml logs -f mysql

# 运行迁移
python migrate.py
```

---

## 数据库操作

### 连接数据库

**SQLite**:
```bash
sqlite3 cxygpt.db
```

**MySQL**:
```bash
docker-compose exec mysql mysql -u cxygpt -pcxygpt123 cxygpt
```

### 常用 SQL 查询

```sql
-- 查看所有表
SHOW TABLES;

-- 查看用户
SELECT * FROM users;

-- 查看会话
SELECT id, name, owner_id, total_tokens, created_at
FROM chat_sessions
ORDER BY updated_at DESC
LIMIT 10;

-- 查看消息数量
SELECT session_id, COUNT(*) as message_count
FROM messages
GROUP BY session_id;

-- 清空表（谨慎！）
TRUNCATE TABLE messages;
TRUNCATE TABLE chat_sessions;
```

---

## 迁移管理（Alembic）

### 创建新迁移

```bash
# 自动生成迁移（检测模型变化）
alembic revision --autogenerate -m "Add new column to users"

# 手动创建迁移
alembic revision -m "Custom migration"
```

### 应用迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade <revision_id>

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### 回滚迁移

```bash
# 回滚一个版本
alembic downgrade -1

# 回滚到特定版本
alembic downgrade <revision_id>

# 回滚到初始状态
alembic downgrade base
```

---

## 数据库架构

### 核心表

#### users（用户表）
- `id`: UUID 主键
- `username`: 用户名（唯一）
- `email`: 邮箱（唯一）
- `hashed_password`: 哈希密码
- `is_active`: 是否激活
- `is_superuser`: 是否超级用户
- `created_at`, `updated_at`: 时间戳

#### chat_sessions（会话表）
- `id`: UUID 主键
- `owner_id`: 用户 ID（外键）
- `department_id`: 部门 ID（外键，可选）
- `name`: 会话名称
- `system_prompt`: 系统提示
- `total_tokens`: 总 token 数
- `pinned`: 是否置顶
- `created_at`, `updated_at`: 时间戳

#### messages（消息表）
- `id`: UUID 主键
- `session_id`: 会话 ID（外键）
- `role`: 角色（system/user/assistant）
- `content`: 消息内容
- `tokens`: token 数
- `created_at`: 时间戳

#### documents（文档表）
- `id`: UUID 主键
- `owner_id`: 用户 ID（外键）
- `department_id`: 部门 ID（外键，可选）
- `title`: 标题
- `content`: 内容
- `file_path`: 文件路径
- `is_public`: 是否公开
- `created_at`, `updated_at`: 时间戳

#### vector_index_meta（向量索引元数据）
- `id`: UUID 主键
- `document_id`: 文档 ID（外键）
- `index_name`: 索引名称
- `embedding_model`: 嵌入模型
- `chunk_size`: 分块大小
- `chunk_count`: 分块数量
- `created_at`, `updated_at`: 时间戳

#### audit_logs（审计日志）
- `id`: UUID 主键
- `user_id`: 用户 ID（外键）
- `action`: 操作类型
- `resource`: 资源类型
- `resource_id`: 资源 ID
- `details`: 详情（JSONB）
- `ip_address`: IP 地址
- `created_at`: 时间戳

---

## 性能优化

### 索引

所有外键和常用查询字段已创建索引：
- `users.username`
- `users.email`
- `chat_sessions.owner_id`
- `chat_sessions.updated_at`
- `messages.session_id`
- `messages.created_at`

### 全文搜索

使用 PostgreSQL 的 GIN 索引：
```sql
-- 搜索消息内容
SELECT * FROM messages
WHERE to_tsvector('english', content) @@ to_tsquery('AI & model');

-- 搜索文档
SELECT * FROM documents
WHERE to_tsvector('english', content) @@ to_tsquery('machine & learning');
```

---

## 备份与恢复

### SQLite

```bash
# 备份
cp cxygpt.db cxygpt.db.backup

# 恢复
cp cxygpt.db.backup cxygpt.db
```

### PostgreSQL

```bash
# 备份
docker-compose exec postgres pg_dump -U cxygpt cxygpt > backup.sql

# 恢复
docker-compose exec -T postgres psql -U cxygpt -d cxygpt < backup.sql
```

---

## 故障排查

### 问题 1：连接失败

**SQLite**:
- 检查文件路径
- 确认有写权限

**PostgreSQL**:
- 确认 Docker 容器运行中
- 检查端口 5432 是否开放
- 验证用户名密码

### 问题 2：迁移失败

```bash
# 查看错误详情
alembic upgrade head --sql

# 重置 Alembic
alembic stamp head
```

### 问题 3：权限错误

```sql
-- PostgreSQL: 授予权限
GRANT ALL PRIVILEGES ON DATABASE cxygpt TO cxygpt;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cxygpt;
```

---

## 相关文档

- **SQLAlchemy 文档**: https://docs.sqlalchemy.org/
- **Alembic 文档**: https://alembic.sqlalchemy.org/
- **PostgreSQL 文档**: https://www.postgresql.org/docs/
