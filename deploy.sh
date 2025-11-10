#!/bin/bash

# CxyGPT 麒麟系统初次部署脚本

echo "========================================="
echo "CxyGPT 初次部署 - 麒麟系统"
echo "========================================="

# 1. 检查Git是否安装
echo "[1] 检查环境依赖..."
if ! command -v git &> /dev/null; then
    echo "❌ Git未安装，请先安装Git"
    echo "运行: sudo yum install -y git"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    echo "参考 DEPLOYMENT.md 文档"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    echo "参考 DEPLOYMENT.md 文档"
    exit 1
fi

echo "✅ 环境检查通过"

# 2. 克隆项目
echo "[2] 克隆项目..."
if [ -d "cxygpt" ]; then
    echo "项目目录已存在，进入目录..."
    cd cxygpt
else
    git clone https://github.com/lllzzzkkk-s/cxygpt.git
    cd cxygpt
fi

# 3. 切换到正确的分支
echo "[3] 切换到 mac-fix 分支..."
git fetch origin mac-fix
git checkout mac-fix
git pull origin mac-fix

# 4. 创建必要的目录
echo "[4] 创建必要目录..."
mkdir -p storage/knowledge
mkdir -p mysql-data
mkdir -p redis-data

# 5. 复制环境配置
echo "[5] 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
else
    echo "✅ .env 文件已存在"
fi

# 6. 设置脚本权限
echo "[6] 设置脚本权限..."
chmod +x *.sh

# 7. 构建镜像
echo "[7] 构建Docker镜像（首次需要较长时间）..."
docker-compose build

# 8. 启动服务
echo "[8] 启动所有服务..."
docker-compose up -d

# 9. 等待服务就绪
echo "[9] 等待服务就绪..."
sleep 10

# 检查服务状态
echo "- 检查MySQL..."
for i in {1..30}; do
    if docker exec cxygpt-mysql mysqladmin ping -h localhost -u root -p123456 --silent 2>/dev/null; then
        echo "  ✅ MySQL就绪"
        break
    fi
    echo "  等待MySQL启动... ($i/30)"
    sleep 2
done

echo "- 检查API网关..."
for i in {1..30}; do
    if curl -f http://localhost:8001/healthz 2>/dev/null; then
        echo "  ✅ API网关就绪"
        break
    fi
    echo "  等待API网关启动... ($i/30)"
    sleep 2
done

echo "- 检查前端..."
for i in {1..30}; do
    if curl -f http://localhost:5173 2>/dev/null; then
        echo "  ✅ 前端就绪"
        break
    fi
    echo "  等待前端启动... ($i/30)"
    sleep 2
done

# 10. 显示服务状态
echo "[10] 服务状态："
docker-compose ps

# 11. 获取系统IP
IP=$(hostname -I | awk '{print $1}')

echo -e "\n========================================="
echo "✅ 部署完成！"
echo ""
echo "访问地址："
echo "  - 主页: http://localhost 或 http://$IP"
echo "  - 前端直连: http://$IP:5173"
echo "  - API文档: http://$IP:8001/docs"
echo ""
echo "默认管理员账号："
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "常用命令："
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  更新系统: ./update.sh"
echo "========================================="