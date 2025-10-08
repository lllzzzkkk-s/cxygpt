# MySQL 数据库配置指南

## 快速开始

### 1. 安装 MySQL

**Windows:**
- 下载 MySQL Installer: https://dev.mysql.com/downloads/installer/
- 安装 MySQL Server 8.0+
- 记住设置的 root 密码

**使用 Docker (推荐):**
```bash
docker run --name cxygpt-mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=cxygpt \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

### 2. 配置数据库连接

编辑 `apps/api-gateway/.env`：

```bash
# MySQL 配置（生产环境推荐）
DATABASE_URL=mysql+aiomysql://root:123456@localhost:3306/cxygpt?charset=utf8mb4

# 如果使用不同的配置，修改对应部分：
# mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
```

### 3. 初始化数据库

```bash
cd apps/api-gateway
python scripts/init_mysql.py
```

输出示例：
```
============================================================
CxyGPT MySQL 数据库初始化
============================================================

📍 数据库配置: localhost:3306/cxygpt

🔧 连接 MySQL: localhost:3306
✅ 数据库 'cxygpt' 创建成功

🔧 开始创建数据库表...
✅ 数据库表创建成功

📊 已创建的表:
  - users
  - departments
  - chat_sessions
  - messages
  - documents
  - vector_index_meta
  - audit_logs

============================================================
✅ 数据库初始化完成！
============================================================
```

### 4. 验证数据库

```bash
# 运行测试
pytest -v

# 启动服务
python -m api_gateway.main
```

## 数据库架构优化

### UUID 存储优化

- **原方案**: `CHAR(36)` 存储 UUID 字符串（36 字节）
- **新方案**: `BINARY(16)` 存储 UUID 二进制（16 字节）
- **节省**: 每个 UUID 节省 20 字节 + 索引优化

### JSON 字段

- 使用原生 `JSON` 类型（MySQL 5.7.8+）
- 支持 JSON 函数和索引
- 比 `TEXT` 存储更高效

### 连接池配置

```python
pool_size=20        # 基础连接池大小
max_overflow=40     # 额外可创建连接数
pool_recycle=3600   # 连接回收时间（1小时）
pool_timeout=30     # 获取连接超时（30秒）
pool_pre_ping=True  # 连接检活
```

### 索引优化

已创建的索引：
- 主键：所有表的 `id` (BINARY(16))
- 外键：所有外键字段
- 查询优化：`username`, `email`, `created_at`, `updated_at`

## 常见问题

### 问题 1: 连接失败

**错误**: `Can't connect to MySQL server`

**解决**:
1. 检查 MySQL 服务是否启动
2. 验证端口 3306 是否开放
3. 确认用户名密码是否正确

### 问题 2: 字符集错误

**错误**: `Incorrect string value`

**解决**:
确保数据库使用 UTF-8MB4：
```sql
ALTER DATABASE cxygpt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 问题 3: 连接池耗尽

**错误**: `QueuePool limit exceeded`

**解决**:
调整 `.env` 中的连接池大小（不推荐，应该优化代码）

## 性能监控

### 查看连接数

```sql
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';
```

### 查看慢查询

```sql
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

### 表大小统计

```sql
SELECT
    table_name AS '表名',
    ROUND(data_length / 1024 / 1024, 2) AS '数据大小(MB)',
    ROUND(index_length / 1024 / 1024, 2) AS '索引大小(MB)'
FROM information_schema.tables
WHERE table_schema = 'cxygpt'
ORDER BY data_length DESC;
```

## 备份与恢复

### 备份数据库

```bash
mysqldump -u root -p cxygpt > backup.sql
```

### 恢复数据库

```bash
mysql -u root -p cxygpt < backup.sql
```

## 从 SQLite 迁移

如果你之前使用 SQLite，需要手动迁移数据：

```bash
# 1. 导出 SQLite 数据
sqlite3 cxygpt.db .dump > sqlite_dump.sql

# 2. 初始化 MySQL
python scripts/init_mysql.py

# 3. 手动导入数据（需要转换 SQL 语法）
# 或使用专用迁移工具
```
