# 🚀 Docker + MySQL 快速安装指南

## 📦 步骤 1: 安装 Docker Desktop

### 方式 A: 自动安装（推荐）

在项目根目录运行：

```powershell
.\install-docker-simple.ps1
```

### 方式 B: 手动安装

1. **下载 Docker Desktop**
   - 官网: https://www.docker.com/products/docker-desktop
   - 直接下载: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

2. **运行安装程序**
   - 双击 `Docker Desktop Installer.exe`
   - 勾选 "Use WSL 2 instead of Hyper-V" (推荐)
   - 等待安装完成（约 5-10 分钟）

3. **重启计算机**（必需）

4. **启动 Docker Desktop**
   - 从开始菜单启动 "Docker Desktop"
   - 接受服务条款
   - 等待 Docker 引擎启动（系统托盘图标变绿）

5. **验证安装**
   ```powershell
   docker --version
   docker compose version
   ```

## 🐬 步骤 2: 启动 MySQL + 运行测试

Docker 安装完成后，运行：

```powershell
# 一键启动 MySQL + 初始化数据库
.\start-mysql.ps1
```

这个脚本会自动：
1. 启动 MySQL 容器（使用 Docker Compose）
2. 创建数据库 `cxygpt`
3. 初始化所有数据表
4. 运行测试验证

## ✅ 验证结果

成功后你会看到：

```
============================================================
OK 全部完成！
============================================================

你现在可以:
  1. 运行测试: pytest -v
  2. 启动服务: python -m api_gateway.main
  3. 停止 MySQL: docker compose -f ../../docker-compose.mysql.yml down
```

## 🔧 手动步骤（如果自动脚本失败）

```powershell
# 1. 启动 MySQL 容器
docker compose -f docker-compose.mysql.yml up -d

# 2. 等待 MySQL 就绪（约 10 秒）
timeout /t 10

# 3. 进入项目目录
cd apps\api-gateway

# 4. 初始化数据库
python scripts\init_mysql.py

# 5. 运行测试
pytest -v
```

## 📊 MySQL 连接信息

```
主机: localhost
端口: 3306
数据库: cxygpt
用户: root
密码: 123456

连接字符串:
mysql+aiomysql://root:123456@localhost:3306/cxygpt?charset=utf8mb4
```

## 🐛 常见问题

### Docker Desktop 启动失败

**解决方案**：
1. 确保 WSL 2 已安装并更新
2. 在 BIOS 中启用虚拟化（Virtualization/VT-x）
3. 重启 Docker Desktop

### MySQL 容器启动失败

**解决方案**：
```powershell
# 停止并删除容器
docker compose -f docker-compose.mysql.yml down -v

# 重新启动
docker compose -f docker-compose.mysql.yml up -d

# 查看日志
docker compose -f docker-compose.mysql.yml logs -f
```

### 端口 3306 被占用

**解决方案**：
```powershell
# 查找占用进程
netstat -ano | findstr :3306

# 停止 MySQL 服务（如果已安装本地 MySQL）
net stop MySQL80

# 或修改 docker-compose.mysql.yml 中的端口映射
```

## 📚 完整文档

- Docker 安装详细指南: `DOCKER_INSTALL.md`
- MySQL 配置说明: `apps/api-gateway/docs/MySQL_SETUP.md`
- 迁移文档: `apps/api-gateway/MYSQL_MIGRATION.md`

## ⏱️ 预计时间

- Docker 下载安装: 15-20 分钟
- MySQL 启动配置: 2-3 分钟
- 运行测试: 1-2 分钟
- **总计**: 约 20-25 分钟

---

**遇到问题？** 查看 `DOCKER_INSTALL.md` 获取详细帮助
