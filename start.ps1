# ========================
# CxyGPT 启动脚本（Windows PowerShell）
# ========================

param(
    [string]$Mode = "single",  # single | multi
    [switch]$Mock,              # 是否使用 Mock 模式
    [switch]$SkipFrontend,      # 跳过前端启动
    [switch]$SkipGateway,       # 跳过网关启动
    [switch]$Help
)

if ($Help) {
    Write-Host "CxyGPT 启动脚本" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法："
    Write-Host "  .\start.ps1 [-Mode single|multi] [-Mock] [-SkipFrontend] [-SkipGateway]"
    Write-Host ""
    Write-Host "参数："
    Write-Host "  -Mode         single（单人模式）或 multi（多人模式），默认 single"
    Write-Host "  -Mock         使用 Mock 模式启动网关（无需 vLLM）"
    Write-Host "  -SkipFrontend 跳过前端启动"
    Write-Host "  -SkipGateway  跳过网关启动"
    Write-Host ""
    Write-Host "示例："
    Write-Host "  .\start.ps1                    # 单人模式启动前端+网关（Mock）"
    Write-Host "  .\start.ps1 -Mode multi        # 多人模式启动"
    Write-Host "  .\start.ps1 -Mock              # Mock 模式快速验证"
    exit 0
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  CxyGPT 启动脚本" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 确定配置文件
$ConfigFile = if ($Mode -eq "multi") { ".env.multi" } else { ".env.single" }
Write-Host "[1/4] 使用配置：$ConfigFile" -ForegroundColor Green

# 启动前端
if (-not $SkipFrontend) {
    Write-Host "[2/4] 启动前端..." -ForegroundColor Green
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd apps\web; npm run dev" -WindowStyle Normal
    Start-Sleep -Seconds 2
} else {
    Write-Host "[2/4] 跳过前端启动" -ForegroundColor Yellow
}

# 复制配置文件到网关目录
Copy-Item $ConfigFile -Destination "apps\api-gateway\.env" -Force

# 如果是 Mock 模式，修改 .env
if ($Mock) {
    Write-Host "[3/4] 启用 Mock 模式" -ForegroundColor Yellow
    (Get-Content "apps\api-gateway\.env") -replace "USE_MOCK=0", "USE_MOCK=1" | Set-Content "apps\api-gateway\.env"
}

# 启动网关
if (-not $SkipGateway) {
    Write-Host "[3/4] 启动网关..." -ForegroundColor Green
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd apps\api-gateway; .\venv\Scripts\Activate.ps1; python -m api_gateway.main" -WindowStyle Normal
    Start-Sleep -Seconds 3
} else {
    Write-Host "[3/4] 跳过网关启动" -ForegroundColor Yellow
}

Write-Host "[4/4] 启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址：" -ForegroundColor Cyan
Write-Host "  前端：      http://localhost:5173" -ForegroundColor White
Write-Host "  Swagger：   http://localhost:8001/docs" -ForegroundColor White
Write-Host "  健康检查：  http://localhost:8001/healthz" -ForegroundColor White
Write-Host ""

if ($Mock) {
    Write-Host "当前为 Mock 模式，无需启动 vLLM" -ForegroundColor Yellow
} else {
    Write-Host "下一步：启动 vLLM" -ForegroundColor Cyan
    Write-Host "  参考 README.md 中的 'vLLM 启动命令' 章节" -ForegroundColor White
    Write-Host ""
    Write-Host "  单人模式（全精度）：" -ForegroundColor Yellow
    Write-Host "    python -m vllm.entrypoints.openai.api_server --model ~/models/Qwen3-14B --dtype bfloat16 --kv-cache-dtype fp8 --max-model-len 3072 --gpu-memory-utilization 0.95 --host 0.0.0.0 --port 8000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  多人模式（4bit量化）：" -ForegroundColor Yellow
    Write-Host "    python -m vllm.entrypoints.openai.api_server --model ~/models/Qwen3-14B-GPTQ-Int4 --dtype auto --kv-cache-dtype fp8 --max-model-len 4096 --gpu-memory-utilization 0.92 --host 0.0.0.0 --port 8000" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
