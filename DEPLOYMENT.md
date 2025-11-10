# CxyGPT 麒麟系统部署指南

## 项目概述
CxyGPT 是一个基于 Docker 的 AI 对话系统，包含前端、后端API网关、MySQL数据库、Redis缓存和Nginx反向代理。

## 系统要求
- 麒麟操作系统（Kylin OS）
- Docker 20.10+ 和 Docker Compose 2.0+
- Git
- 至少 4GB 内存
- 10GB 可用磁盘空间

## 快速部署步骤

### 1. 安装依赖

#### 安装 Docker（麒麟系统）
```bash
# 更新包管理器
sudo yum update -y

# 安装必要的依赖
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

#### 安装 Docker Compose
```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

#### 安装 Git
```bash
sudo yum install -y git
```

### 2. 克隆项目
```bash
# 克隆项目
git clone https://github.com/lllzzzkkk-s/cxygpt.git
cd cxygpt

# 创建必要的目录
mkdir -p storage/knowledge
```

### 3. 配置环境

#### 创建环境文件
```bash
# 复制示例环境文件
cp .env.example .env

# 编辑环境配置（根据需要修改）
vim .env
```

#### 主要配置项说明
```env
# 数据库配置
DATABASE_URL=mysql+aiomysql://root:123456@mysql:3306/cxygpt?charset=utf8mb4

# JWT密钥（生产环境请修改）
JWT_SECRET_KEY=your-secret-key-here

# 单用户/多用户模式
SINGLE_USER=true

# Mock模式（开发测试用）
USE_MOCK=false
```

### 4. 构建和启动服务

#### 一键启动所有服务
```bash
# 构建所有镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

#### 单独管理服务
```bash
# 启动特定服务
docker-compose up -d mysql redis
docker-compose up -d api-gateway
docker-compose up -d web nginx

# 查看日志
docker-compose logs -f api-gateway
docker-compose logs -f web

# 重启服务
docker-compose restart api-gateway
```

### 5. 初始化数据库

数据库会自动初始化，默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

如需手动初始化：
```bash
# 进入API网关容器
docker exec -it cxygpt-gateway bash

# 运行数据库迁移
python -m alembic upgrade head
```

### 6. 访问系统

- 前端界面：http://localhost
- API文档：http://localhost:8001/docs
- 健康检查：http://localhost:8001/healthz

## 生产环境部署

### 1. 使用生产配置
```bash
# 使用生产环境docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. 配置HTTPS（Nginx SSL）
```bash
# 将SSL证书放置到指定目录
cp your-cert.pem infra/nginx/ssl/cert.pem
cp your-key.pem infra/nginx/ssl/key.pem

# 修改nginx配置启用HTTPS
vim infra/nginx/nginx.conf
```

### 3. 数据持久化
```bash
# 备份数据库
docker exec cxygpt-mysql mysqldump -u root -p123456 cxygpt > backup.sql

# 恢复数据库
docker exec -i cxygpt-mysql mysql -u root -p123456 cxygpt < backup.sql
```

### 4. 性能优化
- 调整MySQL连接池大小：修改 `api_gateway/infrastructure/database.py`
- 配置Redis缓存策略
- 根据显存大小调整AI模型配置：修改 `configs/profiles.yaml`

## 常见问题

### 1. Docker权限问题
```bash
# 将当前用户加入docker组
sudo usermod -aG docker $USER
# 重新登录生效
```

### 2. 端口占用
```bash
# 检查端口占用
sudo netstat -tlnp | grep -E "80|443|3306|6379|8001|5173"

# 修改端口配置
vim docker-compose.yml
```

### 3. 内存不足
```bash
# 查看内存使用
docker stats

# 限制容器内存使用
# 在docker-compose.yml中添加：
services:
  api-gateway:
    mem_limit: 1g
```

### 4. 日志管理
```bash
# 清理Docker日志
docker system prune -a

# 配置日志轮转
vim /etc/docker/daemon.json
```
添加：
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

## 监控和维护

### 健康检查脚本
```bash
#!/bin/bash
# healthcheck.sh
curl -f http://localhost:8001/healthz || exit 1
curl -f http://localhost || exit 1
```

### 自动重启配置
```yaml
# docker-compose.yml中已配置
restart: unless-stopped
```

### 日志监控
```bash
# 实时查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api-gateway --tail 100
```

## 开发环境（无Docker）

如果需要本地开发环境：

### Python后端
```bash
cd apps/api-gateway

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m api_gateway.main
```

### 前端
```bash
cd apps/web

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

## 项目结构
```
cxygpt/
├── apps/
│   ├── api-gateway/    # 后端API网关
│   └── web/            # React前端
├── infra/
│   ├── nginx/         # Nginx配置
│   └── postgres/      # PostgreSQL初始化脚本
├── mysql-init/        # MySQL初始化脚本
├── configs/           # 配置文件
├── docker-compose.yml # Docker编排文件
└── DEPLOYMENT.md      # 本文档
```

## 技术支持

遇到问题请查看：
- 项目仓库：https://github.com/lllzzzkkk-s/cxygpt
- 提交Issue：https://github.com/lllzzzkkk-s/cxygpt/issues

## 版本信息
- Python: 3.11
- Node.js: 18+
- MySQL: 8.0
- Redis: 7-alpine
- Nginx: alpine