# Docker Desktop 安装指南

## 📥 下载 Docker Desktop

### 方式 1: 官方网站（推荐）

访问官方网站下载：
- **官网**: https://www.docker.com/products/docker-desktop
- **直接下载**: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

### 方式 2: 使用 winget（Windows 11/10）

```powershell
winget install Docker.DockerDesktop
```

### 方式 3: 使用 Chocolatey

```powershell
choco install docker-desktop
```

## 📋 系统要求

### Windows 10/11 (推荐)
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 或更高)
- 启用 WSL 2（推荐）或 Hyper-V

### 硬件要求
- 64位处理器，支持 SLAT
- 4GB 系统内存（推荐 8GB+）
- BIOS 启用虚拟化

## 🔧 安装步骤

### 1. 下载安装程序

点击下载链接，保存 `Docker Desktop Installer.exe` 到本地

### 2. 运行安装程序

```powershell
# 双击运行安装程序
.\Docker Desktop Installer.exe
```

安装选项：
- ✅ **Use WSL 2 instead of Hyper-V (recommended)** - 推荐选择
- ✅ **Add shortcut to desktop** - 可选

### 3. 等待安装完成

安装过程约需 5-10 分钟

### 4. 重启计算机

安装完成后需要重启系统

### 5. 启动 Docker Desktop

重启后，从开始菜单启动 "Docker Desktop"

### 6. 接受服务条款

首次启动时需要接受 Docker 服务条款

### 7. 验证安装

打开 PowerShell 或 CMD：

```powershell
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker compose version

# 测试 Docker
docker run hello-world
```

期望输出：
```
Docker version 24.0.x, build xxxxx
Docker Compose version v2.x.x
Hello from Docker!
```

## ⚙️ 配置 WSL 2（推荐）

### 启用 WSL 2

```powershell
# 以管理员身份运行 PowerShell

# 1. 启用 WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 2. 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 3. 重启计算机
Restart-Computer

# 4. 下载 WSL 2 内核更新
# 访问: https://aka.ms/wsl2kernel

# 5. 设置 WSL 2 为默认版本
wsl --set-default-version 2
```

## 🐛 常见问题

### 问题 1: WSL 2 安装失败

**解决方案**:
1. 确保 Windows 版本 >= 19041
2. 检查 BIOS 虚拟化是否启用
3. 下载并安装 WSL 2 内核更新: https://aka.ms/wsl2kernel

### 问题 2: Docker Desktop 启动失败

**解决方案**:
```powershell
# 1. 重置 Docker Desktop
# 右键点击系统托盘中的 Docker 图标 -> Troubleshoot -> Reset to factory defaults

# 2. 清理 Docker 数据
Remove-Item -Recurse -Force $env:APPDATA\Docker
Remove-Item -Recurse -Force $env:LOCALAPPDATA\Docker

# 3. 重新启动 Docker Desktop
```

### 问题 3: 权限错误

**解决方案**:
确保你的用户在 "docker-users" 组中：

```powershell
# 以管理员身份运行
net localgroup docker-users "你的用户名" /ADD

# 注销并重新登录
```

### 问题 4: Hyper-V 冲突

如果你使用 VirtualBox 等其他虚拟化软件，可能会冲突。

**解决方案**:
- 使用 WSL 2 模式（推荐）
- 或禁用 Hyper-V 后使用其他虚拟化软件

## 📦 安装完成后

### 配置 Docker Desktop

打开 Docker Desktop -> Settings:

**1. Resources（资源配置）**
```
CPU: 4 核（根据实际情况）
Memory: 4 GB（推荐 8GB）
Swap: 1 GB
Disk: 64 GB（根据需要）
```

**2. Docker Engine（引擎配置）**
保持默认即可

**3. File Sharing（文件共享）**
确保你的项目目录可以被 Docker 访问

## 🚀 快速测试

安装完成后运行：

```powershell
# 1. 测试 Docker
docker run hello-world

# 2. 启动 MySQL
cd H:\project\cxygpt
docker compose -f docker-compose.mysql.yml up -d

# 3. 查看容器状态
docker ps

# 4. 查看日志
docker compose -f docker-compose.mysql.yml logs -f
```

## 📚 下一步

Docker 安装完成后：

```powershell
# 1. 进入项目目录
cd H:\project\cxygpt

# 2. 一键启动 MySQL + 初始化
.\start-mysql.ps1

# 3. 运行测试
cd apps\api-gateway
pytest -v
```

## 🔗 有用的链接

- Docker 官方文档: https://docs.docker.com/desktop/windows/install/
- WSL 2 安装指南: https://docs.microsoft.com/en-us/windows/wsl/install
- Docker Hub: https://hub.docker.com/
- Docker Compose 文档: https://docs.docker.com/compose/

## ⏱️ 预计时间

- 下载: 5-10 分钟（取决于网速）
- 安装: 5-10 分钟
- 配置: 5 分钟
- **总计**: 约 15-25 分钟

---

安装过程中如有任何问题，请告诉我！
