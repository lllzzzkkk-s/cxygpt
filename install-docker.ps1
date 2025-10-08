# Docker Desktop 自动下载脚本

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Docker Desktop 自动下载和安装" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# 下载 URL
$dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$installerPath = "$env:TEMP\DockerDesktopInstaller.exe"

Write-Host "检查 Docker 是否已安装..." -ForegroundColor Yellow

try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Docker 已安装: $dockerVersion`n" -ForegroundColor Green
        Write-Host "你可以直接运行: .\start-mysql.ps1`n" -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "Docker 未安装，开始下载...`n" -ForegroundColor Yellow
}

# 检查 winget
Write-Host "尝试使用 winget 安装..." -ForegroundColor Yellow
try {
    $wingetCheck = Get-Command winget -ErrorAction Stop
    Write-Host "使用 winget 安装 Docker Desktop...`n" -ForegroundColor Green

    winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n============================================================" -ForegroundColor Cyan
        Write-Host "OK Docker Desktop 安装成功！" -ForegroundColor Green
        Write-Host "============================================================`n" -ForegroundColor Cyan
        Write-Host "接下来的步骤:" -ForegroundColor Yellow
        Write-Host "1. 重启计算机" -ForegroundColor White
        Write-Host "2. 启动 Docker Desktop" -ForegroundColor White
        Write-Host "3. 等待 Docker 服务启动（约 1-2 分钟）" -ForegroundColor White
        Write-Host "4. 运行: .\start-mysql.ps1`n" -ForegroundColor White
        exit 0
    }
} catch {
    Write-Host "winget 不可用，使用手动下载方式...`n" -ForegroundColor Yellow
}

# 手动下载
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "下载 Docker Desktop 安装程序" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan
Write-Host "下载地址: $dockerUrl" -ForegroundColor White
Write-Host "保存位置: $installerPath`n" -ForegroundColor White

try {
    Write-Host "开始下载（约 500 MB，请耐心等待）..." -ForegroundColor Yellow

    # 使用 BITS 传输
    Import-Module BitsTransfer
    Start-BitsTransfer -Source $dockerUrl -Destination $installerPath -Description "下载 Docker Desktop"

    Write-Host "OK 下载完成！`n" -ForegroundColor Green

    # 询问是否立即安装
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "准备安装 Docker Desktop" -ForegroundColor Cyan
    Write-Host "============================================================`n" -ForegroundColor Cyan

    $install = Read-Host "是否立即安装？(Y/N)"

    if ($install -eq "Y" -or $install -eq "y") {
        Write-Host "`n开始安装 Docker Desktop..." -ForegroundColor Yellow
        Write-Host "注意：安装过程中请勾选 'Use WSL 2' 选项`n" -ForegroundColor Yellow

        Start-Process -FilePath $installerPath -Wait

        Write-Host "`n============================================================" -ForegroundColor Cyan
        Write-Host "安装完成！" -ForegroundColor Green
        Write-Host "============================================================`n" -ForegroundColor Cyan
        Write-Host "接下来的步骤:" -ForegroundColor Yellow
        Write-Host "1. 重启计算机（必需）" -ForegroundColor White
        Write-Host "2. 启动 Docker Desktop" -ForegroundColor White
        Write-Host "3. 接受服务条款" -ForegroundColor White
        Write-Host "4. 等待 Docker 服务启动" -ForegroundColor White
        Write-Host "5. 运行: docker --version 验证安装" -ForegroundColor White
        Write-Host "6. 运行: .\start-mysql.ps1 启动 MySQL`n" -ForegroundColor White

        # 询问是否重启
        $reboot = Read-Host "是否立即重启计算机？(Y/N)"
        if ($reboot -eq "Y" -or $reboot -eq "y") {
            Write-Host "`n正在重启..." -ForegroundColor Yellow
            Restart-Computer
        }
    } else {
        Write-Host "`n安装程序已保存至: $installerPath" -ForegroundColor Green
        Write-Host "请手动运行安装程序完成安装`n" -ForegroundColor Yellow
    }

} catch {
    Write-Host "`n!! 下载失败: $_" -ForegroundColor Red
    Write-Host "`n请手动下载 Docker Desktop:" -ForegroundColor Yellow
    Write-Host "官网: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "直接下载: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe`n" -ForegroundColor White
    Write-Host "下载完成后双击安装即可`n" -ForegroundColor Yellow

    # 尝试在浏览器中打开下载页面
    $openBrowser = Read-Host "是否在浏览器中打开下载页面？(Y/N)"
    if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
        Start-Process "https://www.docker.com/products/docker-desktop"
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "需要帮助？" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "查看详细安装指南: DOCKER_INSTALL.md" -ForegroundColor White
Write-Host "常见问题解答: https://docs.docker.com/desktop/troubleshoot/overview/`n" -ForegroundColor White
