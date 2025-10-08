# ================================
# 代码质量问题自动修复脚本
# ================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  自动修复代码质量问题" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 进入后端目录
Set-Location apps\api-gateway

# 激活虚拟环境
Write-Host "`n[1/4] 激活虚拟环境..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# 安装开发工具（如果需要）
Write-Host "`n[2/4] 检查开发工具..." -ForegroundColor Yellow
pip install -q ruff black mypy 2>$null

# 运行 Ruff 自动修复
Write-Host "`n[3/4] 运行 Ruff 自动修复..." -ForegroundColor Yellow
ruff check . --fix --unsafe-fixes
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Ruff 修复完成" -ForegroundColor Green
} else {
    Write-Host "!! Ruff 有一些问题无法自动修复" -ForegroundColor Yellow
}

# 运行 Black 格式化
Write-Host "`n[4/4] 运行 Black 格式化..." -ForegroundColor Yellow
black .
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Black 格式化完成" -ForegroundColor Green
} else {
    Write-Host "!! Black 格式化失败" -ForegroundColor Red
}

# 再次检查
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  最终检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nRuff 检查:" -ForegroundColor Yellow
ruff check . --statistics

Write-Host "`nBlack 检查:" -ForegroundColor Yellow
black --check . --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK 所有文件格式正确" -ForegroundColor Green
} else {
    Write-Host "!! 仍有文件需要格式化" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  修复完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location ..\..
