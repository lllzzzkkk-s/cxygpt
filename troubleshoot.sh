#!/bin/bash

# CxyGPT 故障排查脚本
# 用于麒麟系统502错误诊断

echo "========================================="
echo "CxyGPT 系统故障排查"
echo "========================================="

# 1. 检查Docker服务状态
echo -e "\n[1] 检查Docker服务状态..."
systemctl status docker | head -n 3

# 2. 检查所有容器状态
echo -e "\n[2] 检查容器运行状态..."
docker-compose ps

# 3. 检查容器网络
echo -e "\n[3] 检查容器网络连接..."
docker network ls
docker network inspect cxygpt_cxygpt-network 2>/dev/null | grep -A 5 "Containers"

# 4. 测试服务可达性
echo -e "\n[4] 测试服务内部连接..."
echo "- 测试前端服务:"
docker exec cxygpt-nginx curl -I http://web:5173 2>/dev/null | head -n1

echo "- 测试后端服务:"
docker exec cxygpt-nginx curl -I http://api-gateway:8001/healthz 2>/dev/null | head -n1

# 5. 检查端口监听
echo -e "\n[5] 检查端口监听状态..."
netstat -tlnp | grep -E "80|443|5173|8001|3306|6379" 2>/dev/null || ss -tlnp | grep -E "80|443|5173|8001|3306|6379"

# 6. 检查容器日志
echo -e "\n[6] 最近的错误日志..."
echo "- Nginx错误:"
docker logs cxygpt-nginx --tail 10 2>&1 | grep -i error || echo "无错误"

echo "- API网关错误:"
docker logs cxygpt-gateway --tail 10 2>&1 | grep -i error || echo "无错误"

echo "- Web前端错误:"
docker logs cxygpt-web --tail 10 2>&1 | grep -i error || echo "无错误"

# 7. 检查防火墙
echo -e "\n[7] 检查防火墙状态..."
firewall-cmd --list-ports 2>/dev/null || iptables -L INPUT -n | grep -E "80|443|8001|5173"

# 8. 检查SELinux
echo -e "\n[8] 检查SELinux状态..."
getenforce 2>/dev/null || echo "SELinux未安装"

# 9. 资源使用情况
echo -e "\n[9] 检查系统资源..."
echo "- 内存使用:"
free -h | grep Mem

echo "- Docker容器资源:"
docker stats --no-stream

echo -e "\n========================================="
echo "故障排查完成"
echo "========================================="