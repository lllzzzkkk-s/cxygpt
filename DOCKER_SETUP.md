# Docker 部署指南

## 概述

CxyGPT 提供完整的 Docker 容器化部署方案，支持开发和生产环境。本文档整合了 Docker 安装、MySQL 快速启动和完整部署流程。

## 快速开始

### 方式 1: 仅启动 MySQL（最简单）

```powershell
# 一键启动 MySQL
docker-compose -f docker-compose.mysql.yml up -d

# 初始化数据库
cd apps\api-gateway
python scripts\init_mysql_simple.py
```

### 方式 2: 完整开发环境

```powershell
# 启动所有服务（API + Web + MySQL + Redis）
docker-compose -f docker-compose.dev.yml up -d

# 访问前端
start http://localhost:5173

# 访问后端 API
start http://localhost:8000/docs
```

## Docker 安装

### Windows 安装步骤

#### 1. 系统要求

- Windows 10/11 Pro、Enterprise 或 Education（64位）
- 启用 Hyper-V 和 WSL 2
- 至少 4GB RAM

#### 2. 安装 Docker Desktop

**方式 A: 官方安装器**

1. 下载 Docker Desktop
   - 官网: https://www.docker.com/products/docker-desktop
   - 直接下载: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

2. 运行安装器
   ```powershell
   # 以管理员身份运行
   .\Docker Desktop Installer.exe
   ```

3. 安装选项
   - ✅ Use WSL 2 instead of Hyper-V（推荐）
   - ✅ Add shortcut to desktop

4. 重启电脑

**方式 B: 使用 Winget（Windows 包管理器）**

```powershell
# 安装 Docker Desktop
winget install Docker.DockerDesktop

# 或使用 Chocolatey
choco install docker-desktop
```

#### 3. 启用 WSL 2（如需要）

```powershell
# 以管理员身份打开 PowerShell

# 启用 WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启电脑
Restart-Computer

# 安装 WSL 2 Linux 内核更新包
# 下载: https://aka.ms/wsl2kernel

# 设置 WSL 2 为默认版本
wsl --set-default-version 2

# 安装 Ubuntu（可选）
wsl --install -d Ubuntu-22.04
```

#### 4. 验证安装

```powershell
# 检查 Docker 版本
docker --version
# 预期: Docker version 24.0.0 或更高

# 检查 Docker Compose
docker-compose --version
# 预期: Docker Compose version v2.x.x

# 运行测试容器
docker run hello-world
# 预期: Hello from Docker!
```

#### 5. 配置 Docker

打开 Docker Desktop，进入 Settings：

- **General**
  - ✅ Start Docker Desktop when you log in
  - ✅ Use WSL 2 based engine

- **Resources**
  - CPU: 2-4 核
  - Memory: 4-8 GB
  - Disk: 20 GB+

- **Docker Engine** (高级用户)
  ```json
  {
    "registry-mirrors": [
      "https://mirror.example.com"  // 可选：配置镜像加速
    ]
  }
  ```

### Linux 安装（可选参考）

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

## MySQL 快速部署

### 配置文件：docker-compose.mysql.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: cxygpt-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: cxygpt
      MYSQL_USER: cxygpt
      MYSQL_PASSWORD: cxygpt123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  mysql_data:
    driver: local
```

### 使用步骤

```powershell
# 1. 启动 MySQL
docker-compose -f docker-compose.mysql.yml up -d

# 2. 查看日志
docker-compose -f docker-compose.mysql.yml logs -f mysql

# 3. 等待数据库就绪（约 10-30 秒）
# 看到 "ready for connections" 表示启动成功

# 4. 初始化数据库
cd apps\api-gateway
python scripts\init_mysql_simple.py

# 5. 验证连接
docker exec -it cxygpt-mysql mysql -u root -p123456 -e "SHOW DATABASES;"

# 6. 停止 MySQL
docker-compose -f docker-compose.mysql.yml down

# 7. 清理数据（谨慎！）
docker-compose -f docker-compose.mysql.yml down -v
```

### 连接配置

在 `apps/api-gateway/.env` 中配置：

```env
DATABASE_URL=mysql+aiomysql://root:123456@localhost:3306/cxygpt?charset=utf8mb4
```

## 完整开发环境部署

### 配置文件：docker-compose.dev.yml

```yaml
version: '3.8'

services:
  # MySQL 数据库
  mysql:
    image: mysql:8.0
    container_name: cxygpt-mysql
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: cxygpt
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: cxygpt-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # 后端 API
  api-gateway:
    build:
      context: ./apps/api-gateway
      dockerfile: Dockerfile
    container_name: cxygpt-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+aiomysql://root:123456@mysql:3306/cxygpt?charset=utf8mb4
      - REDIS_URL=redis://redis:6379
      - USE_MOCK=true
      - SINGLE_USER=true
    volumes:
      - ./apps/api-gateway:/app
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn api_gateway.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  # 前端 Web
  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    container_name: cxygpt-web
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./apps/web:/app
      - /app/node_modules
    command: npm run dev -- --host
    depends_on:
      - api-gateway

volumes:
  mysql_data:
  redis_data:
```

### 启动完整环境

```powershell
# 1. 构建镜像
docker-compose -f docker-compose.dev.yml build

# 2. 启动所有服务
docker-compose -f docker-compose.dev.yml up -d

# 3. 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 4. 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 5. 初始化数据库
docker exec -it cxygpt-api python scripts/init_mysql_simple.py

# 6. 访问服务
# 前端: http://localhost:5173
# 后端 API: http://localhost:8000/docs
# MySQL: localhost:3306
# Redis: localhost:6379

# 7. 停止服务
docker-compose -f docker-compose.dev.yml down

# 8. 清理所有数据
docker-compose -f docker-compose.dev.yml down -v
```

## 生产环境部署

### 配置文件：docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: cxygpt-mysql-prod
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "${MYSQL_PORT}:3306"
    volumes:
      - mysql_prod_data:/var/lib/mysql
      - ./mysql/conf.d:/etc/mysql/conf.d:ro
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    networks:
      - cxygpt-network

  redis:
    image: redis:7-alpine
    container_name: cxygpt-redis-prod
    restart: always
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - redis_prod_data:/data
    networks:
      - cxygpt-network

  api-gateway:
    image: cxygpt/api-gateway:${VERSION:-latest}
    container_name: cxygpt-api-prod
    restart: always
    ports:
      - "${API_PORT}:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - USE_MOCK=false
      - SINGLE_USER=false
      - LOG_LEVEL=INFO
    depends_on:
      - mysql
      - redis
    networks:
      - cxygpt-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    image: cxygpt/web:${VERSION:-latest}
    container_name: cxygpt-web-prod
    restart: always
    ports:
      - "${WEB_PORT}:80"
    environment:
      - VITE_API_URL=${API_URL}
    depends_on:
      - api-gateway
    networks:
      - cxygpt-network

networks:
  cxygpt-network:
    driver: bridge

volumes:
  mysql_prod_data:
  redis_prod_data:
```

### 生产环境配置 (.env)

```env
# MySQL 配置
MYSQL_ROOT_PASSWORD=your_secure_password_here
MYSQL_DATABASE=cxygpt_prod
MYSQL_USER=cxygpt_user
MYSQL_PASSWORD=your_db_password_here
MYSQL_PORT=3306

# Redis 配置
REDIS_PORT=6379

# API 配置
API_PORT=8000
DATABASE_URL=mysql+aiomysql://cxygpt_user:your_db_password_here@mysql:3306/cxygpt_prod?charset=utf8mb4
REDIS_URL=redis://redis:6379

# Web 配置
WEB_PORT=80
API_URL=https://api.yourdomain.com

# 版本
VERSION=1.0.0
```

### 生产部署步骤

```powershell
# 1. 准备环境变量
Copy-Item .env.example .env
# 编辑 .env 设置生产密码

# 2. 构建生产镜像
docker-compose build

# 3. 推送到私有仓库（可选）
docker tag cxygpt/api-gateway:latest registry.example.com/cxygpt/api:1.0.0
docker push registry.example.com/cxygpt/api:1.0.0

# 4. 启动服务
docker-compose up -d

# 5. 初始化数据库
docker exec -it cxygpt-api-prod python scripts/init_mysql_simple.py

# 6. 检查服务状态
docker-compose ps
docker-compose logs -f

# 7. 配置 Nginx 反向代理（可选）
# 见下文 Nginx 配置
```

## 离线部署

### 导出镜像

```powershell
# 1. 在有网环境导出镜像
docker save mysql:8.0 -o mysql-8.0.tar
docker save redis:7-alpine -o redis-7.tar
docker save cxygpt/api-gateway:latest -o cxygpt-api.tar
docker save cxygpt/web:latest -o cxygpt-web.tar

# 2. 压缩镜像（可选）
Compress-Archive -Path *.tar -DestinationPath cxygpt-images.zip

# 3. 拷贝到离线环境
# 将镜像文件和 docker-compose.yml 拷贝到目标机器
```

### 导入镜像

```powershell
# 在离线环境加载镜像
docker load -i mysql-8.0.tar
docker load -i redis-7.tar
docker load -i cxygpt-api.tar
docker load -i cxygpt-web.tar

# 验证镜像
docker images | findstr cxygpt
docker images | findstr mysql
docker images | findstr redis

# 启动服务
docker-compose up -d
```

## Nginx 反向代理（生产推荐）

### 配置文件：nginx.conf

```nginx
upstream cxygpt_api {
    server localhost:8000;
}

upstream cxygpt_web {
    server localhost:5173;
}

server {
    listen 80;
    server_name yourdomain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL 证书
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 前端
    location / {
        proxy_pass http://cxygpt_web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        proxy_pass http://cxygpt_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API 文档
    location /docs {
        proxy_pass http://cxygpt_api/docs;
    }
}
```

## 常用命令

### 服务管理

```powershell
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker exec -it cxygpt-api bash
docker exec -it cxygpt-mysql mysql -u root -p
```

### 数据管理

```powershell
# 备份 MySQL 数据
docker exec cxygpt-mysql mysqldump -u root -p123456 cxygpt > backup.sql

# 恢复 MySQL 数据
docker exec -i cxygpt-mysql mysql -u root -p123456 cxygpt < backup.sql

# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune
```

### 性能监控

```powershell
# 查看资源使用
docker stats

# 查看特定容器
docker stats cxygpt-api cxygpt-mysql

# 查看日志大小
docker ps -q | ForEach-Object { docker inspect -f '{{.Name}} {{.LogPath}}' $_ }
```

## 故障排查

### 问题 1: 容器无法启动

```powershell
# 查看详细日志
docker-compose logs [service_name]

# 检查端口占用
netstat -ano | findstr :3306
netstat -ano | findstr :8000

# 验证配置
docker-compose config
```

### 问题 2: 数据库连接失败

```powershell
# 检查 MySQL 容器状态
docker ps | findstr mysql

# 测试连接
docker exec -it cxygpt-mysql mysql -u root -p123456 -e "SELECT 1;"

# 检查网络
docker network inspect cxygpt_default
```

### 问题 3: 磁盘空间不足

```powershell
# 查看 Docker 磁盘使用
docker system df

# 清理未使用的资源
docker system prune -a --volumes

# 限制日志大小（在 docker-compose.yml 中）
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 性能优化

### 1. 资源限制

```yaml
services:
  api-gateway:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 2. 健康检查优化

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s      # 检查间隔
  timeout: 10s       # 超时时间
  retries: 3         # 重试次数
  start_period: 40s  # 启动等待时间
```

### 3. 网络优化

```yaml
networks:
  cxygpt-network:
    driver: bridge
    driver_opts:
      com.docker.network.driver.mtu: 1450
```

## 安全建议

1. **密码管理**
   - 使用强密码
   - 定期更换密码
   - 使用 Docker secrets（Swarm）

2. **网络隔离**
   - 使用自定义网络
   - 限制容器间通信

3. **镜像安全**
   - 使用官方镜像
   - 定期更新镜像
   - 扫描漏洞

4. **日志管理**
   - 限制日志大小
   - 集中日志收集
   - 定期清理日志

## 相关文档

- [数据库文档](DATABASE.md) - MySQL 详细配置
- [架构设计](ARCHITECTURE.md) - 系统架构说明
- [快速开始](QUICKSTART.md) - 项目快速启动
- [Docker 官方文档](https://docs.docker.com/)
