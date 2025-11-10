# Windows 迁移排障手册

> 记录在 Windows 11 + Docker Desktop + WSL2 环境下将 `cxygpt` 跑起来时遇到的问题与解决步骤，便于后续团队成员复用。

## 1. 环境准备

- **Docker Desktop** 已安装并处于 `Running` 状态，WSL2 后端已启用（Settings → General → *Use the WSL 2 based engine*）。
- Windows 功能 `Virtual Machine Platform` 与 `Windows Subsystem for Linux` 已勾选，必要时重启系统。
- WSL 发行版（如 Ubuntu）处于 Version 2，可通过 `wsl --list --verbose` 检查。
- 如需代理，确认客户端（如 Clash Verge）允许局域网连接，并记录 HTTP/HTTPS 端口。

## 2. 问题清单

### 2.1 Docker 引擎无法连接
- **症状**：所有 `docker`/`docker compose` 命令报错 `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`。
- **原因**：Docker Desktop 后端未启动或挂起，命名管道不可用。
- **处理步骤**：
  1. 启动 Docker Desktop，等待鲸鱼图标出现 `Running`。
  2. 若已启动但卡住，右键鲸鱼图标选择 *Restart Docker*，或以管理员 PowerShell 执行：
     ```powershell
     Stop-Service com.docker.service
     Start-Service com.docker.service
     ```
  3. 重新执行 `docker version` / `docker compose ps`，确认可连接后继续部署。

### 2.2 `apt-get` 下载镜像失败（网络问题）
- **症状**：构建 `api-gateway` 镜像时 `apt-get install` 报 `Unable to connect to deb.debian.org:http`。
- **原因**：容器无法访问外网，需要通过宿主机代理。
- **处理步骤**：
  1. 在 Clash Verge 等代理工具中开启 *Allow LAN*，确认端口（例：`7892`）。
  2. Docker Desktop → Settings → Resources → Proxies 中，把 HTTP/HTTPS 代理均设置为 `http://host.docker.internal:7892`，保存并重启 Docker。
  3. 如果只想临时配置，可在 PowerShell 中：
     ```powershell
     $env:HTTP_PROXY = "http://host.docker.internal:7892"
     $env:HTTPS_PROXY = $env:HTTP_PROXY
     $env:NO_PROXY = "localhost,127.0.0.1,127.*,192.168.*,10.*,172.16.*,172.17.*,172.18.*,172.19.*,172.20.*,172.21.*,172.22.*,172.23.*,172.24.*,172.25.*,172.26.*,172.27.*,172.28.*,172.29.*,172.30.*,172.31.*,*.local"
     docker compose build api-gateway
     ```
  4. 构建成功后可继续 `docker compose up -d`。

### 2.3 登录接口返回 401
- **症状**：前端或 `curl` 调用 `POST /v1/auth/login` 返回 `401 Unauthorized`。
- **原因**：MySQL 中缺少管理员账号或存储的哈希与 `admin123` 不匹配。
- **处理步骤**：
  1. 查看用户表：
     ```powershell
     docker compose exec mysql `
       mysql -u root -p123456 `
       -e "SELECT username, hashed_password FROM users;" cxygpt
     ```
  2. 若没有 `admin` 行或哈希异常，执行脚本重建：
     ```powershell
     docker compose exec api-gateway python scripts/fix_admin_user.py
     ```
     该脚本会将密码重置为 `admin123`。
  3. 也可重新运行迁移脚本创建表和默认账号：
     ```powershell
     docker compose exec api-gateway python migrate.py
     ```
  4. 使用 `curl` 验证：
     ```powershell
     curl -X POST "http://localhost:8001/v1/auth/login" `
       -H "Content-Type: application/json" `
       --data-raw '{"username":"admin","password":"admin123"}'
     ```

### 2.4 知识库接口 500 / CORS 提示
- **症状**：前端访问知识库抽屉时报 `GET /v1/knowledge/documents 500`，浏览器控制台显示 `No 'Access-Control-Allow-Origin' header`。
- **原因**：真实的后端错误是 `knowledge_documents` 等表不存在（旧数据未迁移），FastAPI 返回 500，浏览器将其视为 CORS 问题。
- **处理步骤**：
  1. 运行 ORM 迁移脚本补建所有表：
     ```powershell
     docker compose exec api-gateway python migrate.py
     ```
  2. 再次确认：
     ```powershell
     docker compose exec mysql `
       mysql -u root -p123456 `
       -e "SHOW TABLES LIKE 'knowledge%';" cxygpt
     ```
  3. 登录后执行：
     ```powershell
     $token = (curl -X POST "http://localhost:8001/v1/auth/login" `
       -H "Content-Type: application/json" `
       --data-raw '{"username":"admin","password":"admin123"}' | ConvertFrom-Json).access_token
     curl -H "Authorization: Bearer $token" http://localhost:8001/v1/knowledge/documents
     ```
     若返回 `[]`，说明接口恢复正常。

## 3. 常用验证命令

| 目的 | 命令 |
| --- | --- |
| 查看容器状态 | `docker compose ps` |
| 实时日志 | `docker compose logs -f api-gateway` |
| 健康检查 | `curl http://localhost:8001/healthz` |
| 登录接口 | `curl -X POST http://localhost:8001/v1/auth/login -H "Content-Type: application/json" --data-raw '{"username":"admin","password":"admin123"}'` |
| 知识库列表 | `curl -H "Authorization: Bearer <token>" http://localhost:8001/v1/knowledge/documents` |

## 4. 目录/文件注意事项

- 知识库文件默认存放在 `storage/knowledge`（容器内路径）。首次使用可执行 `docker compose exec api-gateway mkdir -p storage/knowledge` 创建目录。
- 如需手动修改配置，可参考 `DEPLOYMENT.md`、`DOCKER_SETUP.md` 等文档。
- 建议每次切换分支后重新运行 `docker compose up -d --build`，确保镜像包含最新依赖。

## 5. 参考链接

- FastAPI 路由：`apps/api-gateway/api_gateway/routes/auth.py`、`routes/knowledge.py`
- 数据脚本：`apps/api-gateway/migrate.py`、`scripts/fix_admin_user.py`
- Docker 配置：`docker-compose.yml`

> 如在 Windows 上出现新的兼容性问题，可在此文档继续追加案例。
