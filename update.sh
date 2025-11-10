#!/bin/bash

# CxyGPT 麒麟系统更新脚本
# 用于从GitHub拉取最新代码并更新系统

echo "========================================="
echo "CxyGPT 系统更新"
echo "========================================="

# 1. 检查当前分支
echo "[1] 检查当前分支..."
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

# 2. 拉取最新代码
echo "[2] 从GitHub拉取最新代码..."
echo "正在拉取 mac-fix 分支..."
git fetch origin mac-fix
git checkout mac-fix
git pull origin mac-fix

if [ $? -ne 0 ]; then
    echo "❌ 拉取代码失败，请检查网络连接"
    exit 1
fi

echo "✅ 代码更新成功"

# 3. 检查是否有依赖更新
echo "[3] 检查依赖更新..."
if git diff HEAD@{1} HEAD --name-only | grep -q "requirements.txt\|package.json\|docker-compose.yml\|Dockerfile"; then
    echo "检测到依赖文件变更，需要重新构建镜像"
    REBUILD_NEEDED=true
else
    echo "无依赖变更"
    REBUILD_NEEDED=false
fi

# 4. 停止现有服务
echo "[4] 停止现有服务..."
docker-compose down

# 5. 重新构建（如果需要）
if [ "$REBUILD_NEEDED" = true ]; then
    echo "[5] 重新构建Docker镜像..."
    docker-compose build --no-cache
else
    echo "[5] 跳过镜像构建（无依赖变更）"
fi

# 6. 启动服务
echo "[6] 启动服务..."
docker-compose up -d

# 7. 等待服务就绪
echo "[7] 等待服务就绪..."
sleep 5

# 检查MySQL
echo "- 检查MySQL..."
until docker exec cxygpt-mysql mysqladmin ping -h localhost -u root -p123456 --silent 2>/dev/null; do
    echo "  等待MySQL启动..."
    sleep 2
done
echo "  ✅ MySQL就绪"

# 检查后端
echo "- 检查API网关..."
until curl -f http://localhost:8001/healthz 2>/dev/null; do
    echo "  等待API网关启动..."
    sleep 2
done
echo "  ✅ API网关就绪"

# 检查前端
echo "- 检查前端..."
until curl -f http://localhost:5173 2>/dev/null; do
    echo "  等待前端启动..."
    sleep 2
done
echo "  ✅ 前端就绪"

# 8. 验证服务状态
echo "[8] 服务状态："
docker-compose ps

# 9. 显示更新日志
echo -e "\n[9] 最近的更新内容："
git log --oneline -5

echo -e "\n========================================="
echo "✅ 更新完成！"
echo "访问地址："
echo "  - 主页: http://localhost 或 http://$(hostname -I | awk '{print $1}')"
echo "  - API文档: http://localhost:8001/docs"
echo "========================================="