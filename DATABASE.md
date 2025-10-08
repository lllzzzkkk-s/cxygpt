# 数据库文档

## 概述

CxyGPT 使用 MySQL 8.0 作为生产数据库，通过 SQLAlchemy 异步 ORM 访问。项目经过优化，支持高性能的 UUID 存储和原生 JSON 类型。

## 快速开始

### 方式 1：Docker 部署（推荐）

```powershell
# 启动 MySQL 容器
docker-compose -f docker-compose.mysql.yml up -d

# 初始化数据库
cd apps/api-gateway
python scripts/init_mysql_simple.py
```

### 方式 2：使用现有 MySQL

1. **配置连接字符串**

编辑 `apps/api-gateway/.env`：
```env
DATABASE_URL=mysql+aiomysql://root:123456@localhost:3306/cxygpt?charset=utf8mb4
```

2. **初始化数据库**

```powershell
cd apps/api-gateway
python scripts/init_mysql_simple.py
```

输出示例：
```
============================================================
CxyGPT MySQL Database Initialization
============================================================

Database: localhost:3306/cxygpt

Connecting to MySQL: localhost:3306
Database 'cxygpt' created successfully

Creating database tables...
Database tables created successfully

Created tables:
  - users
  - departments
  - chat_sessions
  - messages
  - documents
  - vector_index_meta
  - audit_logs

============================================================
Database initialization completed!
============================================================
```

## 数据库架构

### 核心表结构

#### 1. users（用户表）
```sql
- id: BINARY(16) PRIMARY KEY        # UUID
- username: VARCHAR(50) UNIQUE      # 用户名
- email: VARCHAR(100) UNIQUE        # 邮箱
- hashed_password: VARCHAR(100)     # 哈希密码
- is_active: BOOLEAN               # 是否激活
- is_superuser: BOOLEAN            # 是否超级用户
- created_at: DATETIME             # 创建时间
- updated_at: DATETIME             # 更新时间
```

#### 2. departments（部门表）
```sql
- id: BINARY(16) PRIMARY KEY
- name: VARCHAR(100) UNIQUE
- created_at: DATETIME
- updated_at: DATETIME
```

#### 3. chat_sessions（会话表）
```sql
- id: BINARY(16) PRIMARY KEY
- owner_id: BINARY(16)             # 外键 -> users.id
- department_id: BINARY(16)        # 外键 -> departments.id
- name: VARCHAR(200)
- system_prompt: TEXT
- total_tokens: INTEGER
- pinned: BOOLEAN
- created_at: DATETIME
- updated_at: DATETIME
```

#### 4. messages（消息表）
```sql
- id: BINARY(16) PRIMARY KEY
- session_id: BINARY(16)           # 外键 -> chat_sessions.id
- role: VARCHAR(20)                # system/user/assistant
- content: TEXT
- tokens: INTEGER
- created_at: DATETIME
```

#### 5. documents（文档表）
```sql
- id: BINARY(16) PRIMARY KEY
- owner_id: BINARY(16)             # 外键 -> users.id
- department_id: BINARY(16)        # 外键 -> departments.id
- title: VARCHAR(200)
- content: TEXT
- file_path: VARCHAR(500)
- is_public: BOOLEAN
- created_at: DATETIME
- updated_at: DATETIME
```

#### 6. vector_index_meta（向量索引元数据）
```sql
- id: BINARY(16) PRIMARY KEY
- document_id: BINARY(16)          # 外键 -> documents.id
- index_name: VARCHAR(100)
- embedding_model: VARCHAR(100)
- chunk_size: INTEGER
- chunk_count: INTEGER
- created_at: DATETIME
- updated_at: DATETIME
```

#### 7. audit_logs（审计日志）
```sql
- id: BINARY(16) PRIMARY KEY
- user_id: BINARY(16)              # 外键 -> users.id
- action: VARCHAR(50)
- resource: VARCHAR(50)
- resource_id: VARCHAR(100)
- details: JSON                    # 原生 JSON 类型
- ip_address: VARCHAR(45)
- created_at: DATETIME
```

## 性能优化

### UUID 存储优化

- **传统方案**: CHAR(36) 存储 UUID 字符串 → 36 字节
- **优化方案**: BINARY(16) 存储 UUID 二进制 → 16 字节
- **节省空间**: 55% (20 字节 / 36 字节)
- **索引性能**: 二进制索引比字符串索引更快

实现方式（`api_gateway/infrastructure/models.py`）：
```python
class UUIDBinary(TypeDecorator):
    """使用 BINARY(16) 存储 UUID"""
    impl = BINARY(16)

    def process_bind_param(self, value, dialect):
        """存储时：字符串 → bytes"""
        if isinstance(value, str):
            return uuid.UUID(value).bytes
        return value

    def process_result_value(self, value, dialect):
        """读取时：bytes → 字符串"""
        if value:
            return str(uuid.UUID(bytes=value))
        return value
```

### JSON 字段优化

- 使用 MySQL 原生 `JSON` 类型（MySQL 5.7.8+）
- 支持 JSON 函数和索引
- 比 TEXT 存储更高效

### 连接池配置（生产级）

```python
# api_gateway/infrastructure/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,           # 基础连接数
    max_overflow=40,        # 额外连接数
    pool_recycle=3600,      # 连接回收时间（1小时）
    pool_timeout=30,        # 获取连接超时
    pool_pre_ping=True,     # 连接检活
)
```

**支持并发**: 最多 60 个并发数据库连接（20 基础 + 40 溢出）

### 索引策略

已创建的索引：
- **主键索引**: 所有表的 `id` (BINARY(16))
- **外键索引**: 所有外键字段
- **查询优化索引**:
  - `users.username`
  - `users.email`
  - `chat_sessions.owner_id`
  - `chat_sessions.updated_at`
  - `messages.session_id`
  - `messages.created_at`
  - `documents.owner_id`
  - `audit_logs.user_id`

## 数据库操作

### 连接数据库

```powershell
# Docker 容器
docker exec -it cxygpt-mysql mysql -u root -p123456 cxygpt

# 本地安装
mysql -u root -p cxygpt
```

### 常用查询

```sql
-- 查看所有表
SHOW TABLES;

-- 查看表结构
DESCRIBE users;

-- 查看用户
SELECT HEX(id), username, email, created_at FROM users;

-- 查看会话（最近10个）
SELECT HEX(id), name, HEX(owner_id), total_tokens, created_at
FROM chat_sessions
ORDER BY updated_at DESC
LIMIT 10;

-- 查看消息统计
SELECT HEX(session_id), COUNT(*) as message_count
FROM messages
GROUP BY session_id
ORDER BY message_count DESC;

-- 查看审计日志（JSON 查询）
SELECT
    HEX(id),
    action,
    resource,
    JSON_EXTRACT(details, '$.method') as method,
    created_at
FROM audit_logs
ORDER BY created_at DESC
LIMIT 20;
```

### 性能监控

```sql
-- 查看当前连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';

-- 查看表大小
SELECT
    table_name AS '表名',
    ROUND(data_length / 1024 / 1024, 2) AS '数据大小(MB)',
    ROUND(index_length / 1024 / 1024, 2) AS '索引大小(MB)',
    table_rows AS '行数'
FROM information_schema.tables
WHERE table_schema = 'cxygpt'
ORDER BY data_length DESC;

-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- 超过2秒的查询
```

## 备份与恢复

### 备份数据库

```powershell
# 完整备份
mysqldump -u root -p cxygpt > backup_$(date +%Y%m%d).sql

# Docker 容器备份
docker exec cxygpt-mysql mysqldump -u root -p123456 cxygpt > backup.sql

# 仅备份结构
mysqldump -u root -p --no-data cxygpt > schema.sql

# 仅备份数据
mysqldump -u root -p --no-create-info cxygpt > data.sql
```

### 恢复数据库

```powershell
# 恢复完整备份
mysql -u root -p cxygpt < backup.sql

# Docker 容器恢复
docker exec -i cxygpt-mysql mysql -u root -p123456 cxygpt < backup.sql
```

## 迁移管理

### 使用 Alembic（可选）

项目当前使用脚本初始化，未来可集成 Alembic 进行版本化迁移：

```powershell
# 初始化 Alembic
cd apps/api-gateway
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Add new column"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 故障排查

### 问题 1：连接失败

**错误**: `Can't connect to MySQL server`

**解决方案**:
1. 检查 MySQL 服务状态
   ```powershell
   docker ps | findstr mysql  # Docker
   Get-Service MySQL80        # Windows 服务
   ```
2. 验证端口开放
   ```powershell
   Test-NetConnection localhost -Port 3306
   ```
3. 确认连接字符串正确（`.env` 文件）

### 问题 2：字符集错误

**错误**: `Incorrect string value`

**解决方案**:
```sql
-- 修改数据库字符集
ALTER DATABASE cxygpt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 修改表字符集
ALTER TABLE messages CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 问题 3：连接池耗尽

**错误**: `QueuePool limit exceeded`

**解决方案**:
1. 检查是否有连接泄漏（未关闭的 session）
2. 调整连接池大小（修改 `database.py`）
3. 使用连接监控：
   ```python
   # 添加到 database.py
   from sqlalchemy import event

   @event.listens_for(engine.sync_engine, "connect")
   def receive_connect(dbapi_conn, connection_record):
       logger.info(f"New connection: {id(dbapi_conn)}")
   ```

### 问题 4：UUID 类型错误

**错误**: `'str' object has no attribute 'hex'`

**解决方案**:
确保使用 `UUIDBinary` 类型，并且传入的 UUID 是字符串格式：
```python
# 正确
user_id = str(uuid.uuid4())

# 错误
user_id = uuid.uuid4()  # UUID 对象
```

## 配置说明

### DATABASE_URL 格式

```
mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
```

### 环境配置示例

```bash
# 开发环境 (Docker)
DATABASE_URL=mysql+aiomysql://root:123456@localhost:3306/cxygpt?charset=utf8mb4

# 生产环境
DATABASE_URL=mysql+aiomysql://cxygpt_user:secure_password@db.example.com:3306/cxygpt_prod?charset=utf8mb4

# 高可用配置（连接池）
DATABASE_URL=mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4&pool_recycle=3600&pool_pre_ping=True
```

### 安全建议

1. **密码管理**: 使用环境变量，不要硬编码
2. **用户权限**: 创建专用数据库用户，限制权限
   ```sql
   CREATE USER 'cxygpt_user'@'%' IDENTIFIED BY 'secure_password';
   GRANT SELECT, INSERT, UPDATE, DELETE ON cxygpt.* TO 'cxygpt_user'@'%';
   FLUSH PRIVILEGES;
   ```
3. **SSL 连接**: 生产环境启用 SSL
   ```
   DATABASE_URL=mysql+aiomysql://user:pass@host:3306/db?ssl_ca=/path/to/ca.pem
   ```

## 从 SQLite 迁移

如果之前使用 SQLite，迁移步骤：

1. **导出 SQLite 数据**
   ```powershell
   sqlite3 cxygpt.db .dump > sqlite_dump.sql
   ```

2. **初始化 MySQL**
   ```powershell
   python scripts/init_mysql_simple.py
   ```

3. **转换并导入数据**（手动调整 SQL 语法）
   - UUID 格式转换
   - 日期时间格式调整
   - 布尔值转换（0/1）

4. **验证数据完整性**
   ```sql
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM chat_sessions;
   SELECT COUNT(*) FROM messages;
   ```

## 相关文档

- [架构设计](ARCHITECTURE.md) - 系统架构说明
- [测试文档](TESTING.md) - 数据库测试指南
- [Docker 部署](DOCKER_SETUP.md) - 容器化部署
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [MySQL 官方文档](https://dev.mysql.com/doc/)

## 维护清单

### 日常维护
- [ ] 定期备份数据库（建议每日）
- [ ] 监控慢查询日志
- [ ] 检查连接池使用情况
- [ ] 清理过期审计日志（可选）

### 性能优化
- [ ] 分析查询执行计划（EXPLAIN）
- [ ] 优化索引策略
- [ ] 考虑表分区（数据量大时）
- [ ] 配置 MySQL 参数优化

### 安全检查
- [ ] 定期更新密码
- [ ] 审查用户权限
- [ ] 启用审计日志
- [ ] 配置防火墙规则
