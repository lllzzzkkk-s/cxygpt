# ========================
# 快速验收脚本（Windows PowerShell）
# ========================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  CxyGPT 快速验收" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: 启动网关
Write-Host "[Step 1/2] 启动 API 网关（Mock 模式）..." -ForegroundColor Yellow
Write-Host ""
Write-Host "请在新终端执行以下命令：" -ForegroundColor White
Write-Host ""
Write-Host "cd apps\api-gateway" -ForegroundColor Green
Write-Host "copy ..\..\env.single .env" -ForegroundColor Green
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "python -m api_gateway.main" -ForegroundColor Green
Write-Host ""
Write-Host "等待网关启动后，访问：http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""

Read-Host "网关启动完成后，按 Enter 继续"

# Step 2: 测试网关
Write-Host ""
Write-Host "[测试] 检查网关是否运行..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/healthz" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 网关运行正常" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 网关未运行，请先启动网关" -ForegroundColor Red
    exit 1
}

# 获取限额
try {
    $limits = Invoke-RestMethod -Uri "http://localhost:8001/v1/limits"
    Write-Host "✅ 当前配置：$($limits.profile)，模式：$(if($limits.single_user){'单人'}else{'多人'})" -ForegroundColor Green
    Write-Host "   输入限制：$($limits.max_input_tokens) tokens，输出限制：$($limits.max_output_tokens) tokens" -ForegroundColor Gray
} catch {
    Write-Host "❌ 无法获取限额信息" -ForegroundColor Red
}

Write-Host ""

# Step 3: 启动前端
Write-Host "[Step 2/2] 启动前端..." -ForegroundColor Yellow
Write-Host ""
Write-Host "请在新终端执行以下命令：" -ForegroundColor White
Write-Host ""
Write-Host "cd apps\web" -ForegroundColor Green
Write-Host "npm run dev" -ForegroundColor Green
Write-Host ""
Write-Host "等待前端启动后，访问：http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

Read-Host "前端启动完成后，按 Enter 继续"

# 验收清单
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  验收清单" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "网关（http://localhost:8001）：" -ForegroundColor Yellow
Write-Host "  □ 访问 /docs 可以看到 Swagger 文档" -ForegroundColor White
Write-Host "  □ GET /healthz 返回 {'ok': true}" -ForegroundColor White
Write-Host "  □ GET /v1/limits 返回限额信息" -ForegroundColor White
Write-Host "  □ POST /v1/chat/completions（stream=false）返回 Mock 消息" -ForegroundColor White
Write-Host ""

Write-Host "前端（http://localhost:5173）：" -ForegroundColor Yellow
Write-Host "  □ 页面正常显示（不是空白）" -ForegroundColor White
Write-Host "  □ 顶栏显示 'CxyGPT' 和绿色状态灯" -ForegroundColor White
Write-Host "  □ 左侧显示会话列表" -ForegroundColor White
Write-Host "  □ 输入框下方显示 '单人模式 · SINGLE_32G'" -ForegroundColor White
Write-Host "  □ 发送 '你好' 可以看到 AI 逐字回复" -ForegroundColor White
Write-Host "  □ 点击设置按钮可以打开设置抽屉" -ForegroundColor White
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "详细验收步骤请查看：QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
