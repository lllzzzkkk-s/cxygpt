# CxyGPT MySQL 快速启动脚本

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CxyGPT MySQL 数据库快速启动" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# 检查 Docker
Write-Host "检查 Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "OK Docker 已安装`n" -ForegroundColor Green
} catch {
    Write-Host "!! Docker 未安装" -ForegroundColor Red
    Write-Host "`n请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop`n" -ForegroundColor Yellow
    exit 1
}

# 启动 MySQL
Write-Host "启动 MySQL 容器..." -ForegroundColor Yellow
docker-compose -f docker-compose.mysql.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK MySQL 启动成功`n" -ForegroundColor Green

    Write-Host "等待 MySQL 就绪..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10

    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "MySQL 连接信息" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "主机: localhost" -ForegroundColor White
    Write-Host "端口: 3306" -ForegroundColor White
    Write-Host "数据库: cxygpt" -ForegroundColor White
    Write-Host "用户: root / cxygpt" -ForegroundColor White
    Write-Host "密码: 123456 / cxygpt123" -ForegroundColor White
    Write-Host "`n连接字符串:" -ForegroundColor Yellow
    Write-Host "mysql+aiomysql://root:123456@localhost:3306/cxygpt?charset=utf8mb4`n" -ForegroundColor Green

    # 初始化数据库
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "初始化数据库表" -ForegroundColor Cyan
    Write-Host "============================================================`n" -ForegroundColor Cyan

    Set-Location "apps\api-gateway"

    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1

    Write-Host "运行初始化脚本..." -ForegroundColor Yellow
    python scripts\init_mysql.py

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n============================================================" -ForegroundColor Cyan
        Write-Host "OK 全部完成！" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "`n你现在可以:" -ForegroundColor Yellow
        Write-Host "  1. 运行测试: pytest -v" -ForegroundColor White
        Write-Host "  2. 启动服务: python -m api_gateway.main" -ForegroundColor White
        Write-Host "  3. 停止 MySQL: docker-compose -f ../../docker-compose.mysql.yml down`n" -ForegroundColor White
    } else {
        Write-Host "`n!! 数据库初始化失败" -ForegroundColor Red
        Write-Host "请检查 MySQL 是否正常启动`n" -ForegroundColor Yellow
    }

} else {
    Write-Host "!! MySQL 启动失败`n" -ForegroundColor Red
}
