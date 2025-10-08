# 🎉 MySQL 数据库迁移完成

## ✅ 已完成的优化

### 1. 数据库驱动升级
- ✅ 安装 `aiomysql` + `pymysql` 异步驱动
- ✅ 移除 SQLite/PostgreSQL 依赖

### 2. ORM 模型优化
- ✅ 使用 `BINARY(16)` 存储 UUID（节省 55% 空间）
- ✅ 使用原生 `JSON` 类型（MySQL 5.7.8+）
- ✅ 自定义 `UUIDBinary` 类型转换器

### 3. 连接池优化
- ✅ 基础连接数: 20
- ✅ 最大连接数: 60
- ✅ 连接回收: 1小时
- ✅ 连接检活: 启用
- ✅ 获取超时: 30秒

### 4. 配置文件更新
- ✅ `.env` - MySQL 连接字符串
- ✅ `.env.example` - 配置示例
- ✅ `config.py` - 默认值更新

### 5. 工具脚本
- ✅ `scripts/init_mysql.py` - 数据库初始化
- ✅ `start-mysql.ps1` - 一键启动 MySQL
- ✅ `docker-compose.mysql.yml` - Docker 快速部署

### 6. 文档
- ✅ `docs/MySQL_SETUP.md` - 详细配置指南

## 🚀 快速开始

### 方式 1：使用 Docker（推荐）

```powershell
# 一键启动 MySQL + 初始化数据库
.\start-mysql.ps1
```

### 方式 2：使用现有 MySQL

```powershell
# 1. 修改 .env 配置
DATABASE_URL=mysql+aiomysql://user:password@host:port/dbname?charset=utf8mb4

# 2. 初始化数据库
cd apps/api-gateway
python scripts/init_mysql.py
```

## 📊 数据库架构

### 表结构（7张表）

```
users                 # 用户表
├── id (BINARY(16))  # UUID 主键
├── username         # 用户名（唯一索引）
├── email            # 邮箱（唯一索引）
└── ...

departments          # 部门表
├── id (BINARY(16))
└── name

chat_sessions        # 会话表
├── id (BINARY(16))
├── owner_id         # 外键 -> users.id
├── department_id    # 外键 -> departments.id
└── ...

messages             # 消息表
├── id (BINARY(16))
├── session_id       # 外键 -> chat_sessions.id
└── ...

documents            # 文档表
├── id (BINARY(16))
├── owner_id         # 外键 -> users.id
└── ...

vector_index_meta    # 向量索引元数据
├── id (BINARY(16))
├── document_id      # 外键 -> documents.id
└── ...

audit_logs           # 审计日志
├── id (BINARY(16))
├── user_id          # 外键 -> users.id
├── details (JSON)   # 原生 JSON 字段
└── ...
```

## 🔧 验证安装

```powershell
# 运行测试
cd apps/api-gateway
pytest -v

# 启动服务
python -m api_gateway.main
```

## 📈 性能提升

### 存储优化
- **UUID**: CHAR(36) → BINARY(16) = 节省 55%
- **JSON**: TEXT → JSON = 支持索引和函数
- **总体**: 预计节省 30-40% 存储空间

### 查询优化
- 所有外键创建索引
- 常用查询字段创建索引
- 连接池预热和检活

### 并发优化
- 连接池: 20 基础 + 40 溢出
- 支持 60 并发数据库连接
- 适合中等规模生产环境

## 🛠️ 常用命令

```powershell
# 启动 MySQL（Docker）
docker-compose -f docker-compose.mysql.yml up -d

# 停止 MySQL
docker-compose -f docker-compose.mysql.yml down

# 查看日志
docker-compose -f docker-compose.mysql.yml logs -f

# 连接 MySQL
docker exec -it cxygpt-mysql mysql -u root -p123456 cxygpt

# 初始化数据库
python scripts/init_mysql.py

# 运行测试
pytest -v

# 运行测试（带覆盖率）
pytest -v --cov=api_gateway --cov-report=html
```

## 📝 配置说明

### DATABASE_URL 格式

```
mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
```

### 示例配置

```bash
# 本地开发
DATABASE_URL=mysql+aiomysql://root:123456@localhost:3306/cxygpt?charset=utf8mb4

# Docker 容器
DATABASE_URL=mysql+aiomysql://cxygpt:cxygpt123@localhost:3306/cxygpt?charset=utf8mb4

# 生产环境（建议使用环境变量）
DATABASE_URL=mysql+aiomysql://prod_user:secure_pass@db.example.com:3306/cxygpt_prod?charset=utf8mb4
```

## ⚠️ 注意事项

1. **字符集**: 必须使用 `utf8mb4` 支持完整 Unicode
2. **连接池**: 根据实际负载调整 `pool_size` 和 `max_overflow`
3. **备份**: 生产环境请定期备份数据库
4. **密码**: 不要在代码中硬编码密码，使用环境变量

## 🔄 从 SQLite 迁移

如需从 SQLite 迁移到 MySQL：

1. 导出 SQLite 数据
2. 初始化 MySQL 数据库
3. 使用工具转换 SQL 语法并导入
4. 验证数据完整性

详细步骤参考: `docs/MySQL_SETUP.md`

## 📚 相关文档

- [MySQL 配置指南](docs/MySQL_SETUP.md)
- [数据库架构设计](docs/DATABASE_DESIGN.md)
- [性能优化指南](docs/PERFORMANCE.md)

## ❓ 常见问题

### Q: 为什么选择 MySQL？
A: MySQL 更适合生产环境，支持原生 JSON、BINARY UUID、更好的并发性能。

### Q: 可以继续使用 SQLite 吗？
A: 可以，代码兼容 SQLite，但测试可能失败（UUID 类型问题）。

### Q: 如何调整连接池大小？
A: 修改 `api_gateway/infrastructure/database.py` 中的 `pool_size` 和 `max_overflow`。

## 🎯 下一步

1. ✅ MySQL 数据库已配置
2. ⏭️ 运行测试验证集成
3. ⏭️ 启动服务测试接口
4. ⏭️ 前端集成测试
5. ⏭️ 性能压测
6. ⏭️ 生产部署

---

**最后更新**: 2025-01-06
**维护者**: CxyGPT Team
