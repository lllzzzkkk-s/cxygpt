#!/bin/bash

# CxyGPT 502错误修复脚本
# 适用于麒麟系统

echo "========================================="
echo "CxyGPT 502错误修复"
echo "========================================="

# 1. 停止所有服务
echo "[1] 停止现有服务..."
docker-compose down

# 2. 清理Docker网络
echo "[2] 清理并重建网络..."
docker network prune -f
docker network create cxygpt-network 2>/dev/null

# 3. 重新构建镜像
echo "[3] 重新构建镜像..."
docker-compose build --no-cache

# 4. 按顺序启动服务
echo "[4] 按顺序启动服务..."

# 先启动数据库和缓存
echo "- 启动MySQL和Redis..."
docker-compose up -d mysql redis
sleep 10

# 检查MySQL是否就绪
echo "- 等待MySQL就绪..."
until docker exec cxygpt-mysql mysqladmin ping -h localhost -u root -p123456 --silent; do
    echo "等待MySQL启动..."
    sleep 2
done
echo "MySQL已就绪"

# 启动后端
echo "- 启动API网关..."
docker-compose up -d api-gateway
sleep 5

# 检查后端健康状态
echo "- 检查后端健康状态..."
until docker exec cxygpt-gateway curl -f http://localhost:8001/healthz 2>/dev/null; do
    echo "等待后端启动..."
    sleep 2
done
echo "后端已就绪"

# 启动前端
echo "- 启动Web前端..."
docker-compose up -d web
sleep 5

# 最后启动Nginx
echo "- 启动Nginx..."
docker-compose up -d nginx
sleep 3

# 5. 验证服务
echo "[5] 验证服务状态..."
docker-compose ps

# 6. 测试连接
echo "[6] 测试服务连接..."
curl -I http://localhost/healthz 2>/dev/null | head -n1
curl -I http://localhost 2>/dev/null | head -n1

echo "========================================="
echo "修复完成！"
echo "如果仍有问题，请运行 ./troubleshoot.sh 查看详细信息"
echo "========================================="