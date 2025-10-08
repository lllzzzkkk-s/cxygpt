# ================================
# CxyGPT Docker 快速启动指南
# ================================

## 开发环境（推荐）

### 启动所有服务

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 查看日志

```bash
# 所有服务
docker-compose -f docker-compose.dev.yml logs -f

# 特定服务
docker-compose -f docker-compose.dev.yml logs -f api-gateway
docker-compose -f docker-compose.dev.yml logs -f web
```

### 停止服务

```bash
docker-compose -f docker-compose.dev.yml down
```

### 清理数据（重置数据库）

```bash
docker-compose -f docker-compose.dev.yml down -v
```

---

## 生产环境

### 启动

```bash
docker-compose up -d
```

### 扩展服务

```bash
# 扩展 API 网关到 3 个实例
docker-compose up -d --scale api-gateway=3
```

### 停止

```bash
docker-compose down
```

---

## 访问地址

- **前端**：http://localhost:5173
- **API 网关**：http://localhost:8001
- **Swagger 文档**：http://localhost:8001/docs
- **PostgreSQL**：localhost:5432
- **Redis**：localhost:6379

---

## 健康检查

```bash
# 检查所有服务状态
docker-compose ps

# 检查特定服务健康状态
docker-compose exec api-gateway curl http://localhost:8001/healthz
```

---

## 数据库管理

### 连接 PostgreSQL

```bash
docker-compose exec postgres psql -U cxygpt -d cxygpt
```

### 执行 SQL 文件

```bash
docker-compose exec -T postgres psql -U cxygpt -d cxygpt < your_script.sql
```

### 备份数据库

```bash
docker-compose exec postgres pg_dump -U cxygpt cxygpt > backup.sql
```

### 恢复数据库

```bash
docker-compose exec -T postgres psql -U cxygpt -d cxygpt < backup.sql
```

---

## 常见问题

### Q1: 端口冲突

如果端口已被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8002:8001"  # 将宿主机端口改为 8002
```

### Q2: 构建失败

清理缓存重新构建：

```bash
docker-compose build --no-cache
```

### Q3: 查看容器内部

```bash
docker-compose exec api-gateway sh
```

---

## 环境变量

在项目根目录创建 `.env` 文件：

```env
# 模式
SINGLE_USER=1
FORCE_PROFILE=SINGLE_32G

# vLLM
UPSTREAM_OPENAI_BASE=http://vllm:8000
USE_MOCK=0

# 数据库
POSTGRES_USER=cxygpt
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=cxygpt

# Redis
REDIS_PASSWORD=your_redis_password
```

---

## 监控

### 查看资源使用

```bash
docker stats
```

### 查看特定容器资源

```bash
docker stats cxygpt-gateway cxygpt-web
```

---

## 更新镜像

```bash
# 拉取最新镜像
docker-compose pull

# 重新构建自定义镜像
docker-compose build

# 重启服务
docker-compose up -d
```
