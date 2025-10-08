# ================================
# 🎯 完整验收方案
# ================================

## 📋 验收检查清单

### ✅ 第一部分: 环境准备 (5 分钟)
- [ ] Python 3.11+ 已安装
- [ ] Node.js 20+ 已安装
- [ ] Docker Desktop 已安装并运行
- [ ] Git 已安装

### ✅ 第二部分: 后端验收 (15 分钟)
- [ ] 安装后端依赖
- [ ] 运行代码质量检查
- [ ] 运行单元测试
- [ ] 运行集成测试
- [ ] 检查测试覆盖率
- [ ] 启动后端服务

### ✅ 第三部分: 前端验收 (10 分钟)
- [ ] 安装前端依赖
- [ ] 运行代码质量检查
- [ ] 运行前端测试
- [ ] 检查测试覆盖率
- [ ] 构建前端

### ✅ 第四部分: Docker 验收 (10 分钟)
- [ ] 构建 Docker 镜像
- [ ] 启动 Docker Compose
- [ ] 验证服务健康
- [ ] 测试端到端功能

### ✅ 第五部分: Pre-commit 验收 (5 分钟)
- [ ] 安装 pre-commit hooks
- [ ] 运行所有 hooks
- [ ] 测试提交流程

### ✅ 第六部分: 文档验收 (5 分钟)
- [ ] 检查文档完整性
- [ ] 验证链接有效性

---

# 🚀 详细验收步骤

## 第一部分: 环境检查

### 1.1 检查 Python 版本

```powershell
python --version
# 预期输出: Python 3.11.x 或 3.12.x
```

### 1.2 检查 Node.js 版本

```powershell
node --version
# 预期输出: v20.x.x 或更高

npm --version
# 预期输出: 10.x.x 或更高
```

### 1.3 检查 Docker 版本

```powershell
docker --version
# 预期输出: Docker version 24.x.x 或更高

docker-compose --version
# 预期输出: Docker Compose version v2.x.x 或更高
```

### 1.4 检查 Git 版本

```powershell
git --version
# 预期输出: git version 2.x.x 或更高
```

**✅ 验收标准**: 所有工具版本符合要求

---

## 第二部分: 后端验收

### 2.1 进入后端目录

```powershell
cd H:\project\cxygpt\apps\api-gateway
```

### 2.2 创建并激活虚拟环境

```powershell
# 如果虚拟环境不存在，创建它
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 验证虚拟环境激活
# 命令提示符应该显示 (.venv)
```

### 2.3 安装所有依赖

```powershell
# 安装生产依赖
pip install -r requirements.txt

# 安装测试依赖
pip install -r requirements-test.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 验证安装
pip list
```

**预期输出**: 应该看到 fastapi, uvicorn, sqlalchemy, pytest, black, ruff 等包

### 2.4 运行代码质量检查

```powershell
# 运行 Ruff 检查
ruff check .

# 预期输出: All checks passed! 或具体的警告信息
```

```powershell
# 运行 Black 格式检查
black --check .

# 预期输出: All done! ✨ 🍰 ✨
# 或 "would reformat" 信息（如果有格式问题）
```

```powershell
# 运行 MyPy 类型检查（可能有一些警告，正常）
mypy api_gateway --ignore-missing-imports
```

**✅ 验收标准**:
- Ruff 无严重错误
- Black 格式检查通过
- MyPy 无严重类型错误

### 2.5 运行单元测试

```powershell
# 运行所有单元测试
pytest tests/unit/ -v

# 预期输出: 应该看到所有测试通过
# tests/unit/test_entities.py::TestMessage::test_create_message PASSED
# tests/unit/test_entities.py::TestMessage::test_message_role_enum PASSED
# ... 更多测试 ...
# ==================== XX passed in X.XXs ====================
```

**✅ 验收标准**: 所有单元测试通过（大约 22 个测试）

### 2.6 运行集成测试

```powershell
# 运行集成测试
pytest tests/integration/ -v

# 预期输出: 所有集成测试通过
# tests/integration/test_repositories.py::... PASSED
# ==================== XX passed in X.XXs ====================
```

**✅ 验收标准**: 所有集成测试通过（大约 6 个测试）

### 2.7 运行完整测试并生成覆盖率报告

```powershell
# 运行所有测试并生成覆盖率
pytest --cov=api_gateway --cov-report=html --cov-report=term-missing

# 预期输出:
# ==================== test session starts ====================
# ... 测试运行 ...
# ----------- coverage: platform win32, python 3.11.x -----------
# Name                                    Stmts   Miss  Cover   Missing
# ---------------------------------------------------------------------
# api_gateway/__init__.py                     0      0   100%
# api_gateway/domain/entities.py            XX     XX    XX%
# ... 更多文件 ...
# ---------------------------------------------------------------------
# TOTAL                                     XXX    XXX    XX%
# ==================== XX passed in X.XXs ====================
```

```powershell
# 打开覆盖率 HTML 报告
start htmlcov/index.html
```

**✅ 验收标准**:
- 所有测试通过（约 28 个测试）
- 整体覆盖率接近或超过 70%

### 2.8 启动后端服务（简单验证）

```powershell
# 设置环境变量
$env:USE_MOCK="true"
$env:SINGLE_USER="true"

# 启动服务
uvicorn api_gateway.main:app --reload

# 预期输出:
# INFO:     Started server process [XXXX]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

**在新的 PowerShell 窗口测试 API**:

```powershell
# 测试健康检查
curl http://localhost:8000/health

# 预期输出:
# {"status":"ok","timestamp":"..."}

# 测试限流信息
curl http://localhost:8000/v1/limits

# 预期输出:
# {"max_input_tokens":3072,"max_output_tokens":512,...}

# 访问 API 文档
start http://localhost:8000/docs
```

**✅ 验收标准**:
- 服务启动无错误
- 健康检查返回 200
- API 文档可访问
- 限流信息正确返回

**停止服务**: 按 `Ctrl+C`

---

## 第三部分: 前端验收

### 3.1 进入前端目录

```powershell
# 打开新的 PowerShell 窗口
cd H:\project\cxygpt\apps\web
```

### 3.2 安装依赖

```powershell
# 安装所有依赖
npm install

# 预期输出:
# added XXX packages in XXs
```

### 3.3 运行代码质量检查

```powershell
# 运行 ESLint
npm run lint

# 预期输出:
# ✓ XX files linted
# 或具体的 lint 警告
```

```powershell
# 运行 Prettier 检查
npx prettier --check .

# 预期输出:
# Checking formatting...
# All matched files use Prettier code style!
```

```powershell
# 运行 TypeScript 类型检查
npx tsc --noEmit

# 预期输出: 无错误，或具体的类型错误
```

**✅ 验收标准**:
- ESLint 无严重错误
- Prettier 格式检查通过
- TypeScript 无严重类型错误

### 3.4 运行前端测试

```powershell
# 运行所有测试
npm run test:run

# 预期输出:
# ✓ src/types/index.test.ts (3 tests) 2ms
# ✓ src/lib/openai.test.ts (6 tests) 2ms
# ✓ src/components/TopBar.test.tsx (3 tests) 130ms
#
# Test Files  3 passed (3)
# Tests      12 passed (12)
```

**✅ 验收标准**: 所有 12 个测试通过

### 3.5 生成测试覆盖率报告

```powershell
# 运行覆盖率测试
npm run test:coverage

# 预期输出:
# ✓ src/types/index.test.ts (3 tests)
# ✓ src/lib/openai.test.ts (6 tests)
# ✓ src/components/TopBar.test.tsx (3 tests)
#
# % Coverage report from v8
# ------------------------------------|---------|----------|---------|---------|
# File                                | % Stmts | % Branch | % Funcs | % Lines |
# ------------------------------------|---------|----------|---------|---------|
# All files                           |   XX.XX |    XX.XX |   XX.XX |   XX.XX |
# ...
```

```powershell
# 打开覆盖率报告
start coverage/index.html
```

**✅ 验收标准**: 整体覆盖率接近或超过 70%

### 3.6 构建前端

```powershell
# 构建生产版本
npm run build

# 预期输出:
# vite v7.1.7 building for production...
# ✓ XXX modules transformed.
# dist/index.html                   X.XX kB │ gzip:  X.XX kB
# dist/assets/index-XXXXXXXX.css   XX.XX kB │ gzip: XX.XX kB
# dist/assets/index-XXXXXXXX.js   XXX.XX kB │ gzip: XX.XX kB
# ✓ built in XXXXms
```

**✅ 验收标准**:
- 构建成功
- dist 目录生成
- 无严重警告

### 3.7 预览构建结果

```powershell
# 预览构建版本
npm run preview

# 预期输出:
# Local:   http://localhost:4173/
```

访问 http://localhost:4173/ 查看前端

**✅ 验收标准**: 前端可以正常访问并渲染

**停止服务**: 按 `Ctrl+C`

---

## 第四部分: Docker 验收

### 4.1 返回项目根目录

```powershell
cd H:\project\cxygpt
```

### 4.2 准备环境文件

```powershell
# 复制环境文件
Copy-Item ".env.single" -Destination ".env"

# 验证环境文件
cat .env
```

**✅ 验收标准**: .env 文件存在且包含正确配置

### 4.3 启动开发环境

```powershell
# 使用开发配置启动
docker-compose -f docker-compose.dev.yml up -d

# 预期输出:
# Creating network "cxygpt_default" ...
# Creating cxygpt-postgres ... done
# Creating cxygpt-redis     ... done
# Creating cxygpt-api       ... done
# Creating cxygpt-web       ... done
```

### 4.4 检查服务状态

```powershell
# 查看所有服务状态
docker-compose -f docker-compose.dev.yml ps

# 预期输出: 所有服务都是 "Up" 状态
# NAME               STATUS
# cxygpt-api         Up (healthy)
# cxygpt-web         Up
# cxygpt-postgres    Up (healthy)
# cxygpt-redis       Up (healthy)
```

### 4.5 检查服务日志

```powershell
# 查看 API 日志
docker-compose -f docker-compose.dev.yml logs api-gateway

# 预期输出: 应该看到服务启动日志，无错误
```

```powershell
# 查看 Web 日志
docker-compose -f docker-compose.dev.yml logs web

# 预期输出: 应该看到 Vite 服务启动
```

### 4.6 测试服务端点

```powershell
# 测试后端健康检查
curl http://localhost:8000/health

# 预期输出: {"status":"ok",...}

# 测试前端
start http://localhost:5173

# 预期: 浏览器打开前端页面
```

### 4.7 测试数据库连接

```powershell
# 进入 API 容器
docker exec -it cxygpt-api bash

# 在容器内运行 Python
python

# 在 Python 中测试数据库
>>> from api_gateway.infrastructure.database import async_engine
>>> import asyncio
>>> asyncio.run(async_engine.connect())
# 应该无错误

>>> exit()
>>> exit
```

**✅ 验收标准**:
- 所有服务启动成功
- 健康检查通过
- 前端可访问
- 数据库连接正常

### 4.8 端到端测试

**在浏览器中测试** (http://localhost:5173):

1. ✅ 页面加载无错误
2. ✅ 顶部栏显示 "CxyGPT"
3. ✅ 健康状态指示器显示（灰色/绿色圆点）
4. ✅ 侧边栏显示会话列表
5. ✅ 点击 "新建对话" 创建会话
6. ✅ 在输入框输入消息 "你好"
7. ✅ 发送消息（使用 Mock 模式会返回模拟响应）
8. ✅ 消息显示在聊天窗口
9. ✅ 打开设置面板，调整参数
10. ✅ 设置保存成功

**API 文档测试** (http://localhost:8000/docs):

1. ✅ 打开 Swagger UI
2. ✅ 测试 GET /health
3. ✅ 测试 GET /v1/limits
4. ✅ 测试 POST /v1/chat/completions (使用 Mock 模式)

### 4.9 停止服务

```powershell
# 停止所有服务
docker-compose -f docker-compose.dev.yml down

# 预期输出:
# Stopping cxygpt-web       ... done
# Stopping cxygpt-api       ... done
# Stopping cxygpt-redis     ... done
# Stopping cxygpt-postgres  ... done
# Removing cxygpt-web       ... done
# Removing cxygpt-api       ... done
# Removing cxygpt-redis     ... done
# Removing cxygpt-postgres  ... done
```

**✅ 验收标准**:
- Docker Compose 启动成功
- 所有服务健康
- 端到端功能正常
- 服务可以正常停止

---

## 第五部分: Pre-commit Hooks 验收

### 5.1 安装 Pre-commit

```powershell
# 在后端虚拟环境中安装
cd H:\project\cxygpt\apps\api-gateway
.\.venv\Scripts\Activate.ps1

pip install pre-commit

# 返回项目根目录
cd H:\project\cxygpt
```

### 5.2 安装 Git Hooks

```powershell
# 安装 pre-commit hooks
pre-commit install

# 预期输出:
# pre-commit installed at .git/hooks/pre-commit

# 安装 commit-msg hook
pre-commit install --hook-type commit-msg

# 预期输出:
# pre-commit installed at .git/hooks/commit-msg
```

### 5.3 运行所有 Hooks（首次运行会较慢）

```powershell
# 对所有文件运行 hooks
pre-commit run --all-files

# 预期输出:
# black....................................................................Passed
# ruff.....................................................................Passed
# ruff-format..............................................................Passed
# mypy.....................................................................Passed
# prettier.................................................................Passed
# eslint...................................................................Passed
# trailing-whitespace......................................................Passed
# end-of-file-fixer........................................................Passed
# check-yaml...............................................................Passed
# check-json...............................................................Passed
# check-toml...............................................................Passed
# check-added-large-files..................................................Passed
# check-merge-conflict.....................................................Passed
# detect-private-key.......................................................Passed
# detect-secrets...........................................................Passed
```

**注意**: 首次运行会下载工具，可能需要几分钟

**✅ 验收标准**:
- 所有 hooks 安装成功
- 所有 hooks 检查通过（或只有少量警告）

### 5.4 测试提交流程

```powershell
# 创建一个测试文件
echo "# Test" > test-acceptance.md

# 添加到 Git
git add test-acceptance.md

# 尝试提交（hooks 会自动运行）
git commit -m "test: verify pre-commit hooks"

# 预期输出:
# black....................................................................Passed
# ruff.....................................................................Passed
# ... 更多 hooks ...
# [branch XXXXXXX] test: verify pre-commit hooks
#  1 file changed, 1 insertion(+)
```

```powershell
# 清理测试文件
git reset HEAD~1
Remove-Item test-acceptance.md
```

**✅ 验收标准**:
- Pre-commit hooks 在提交时自动运行
- 提交成功

---

## 第六部分: 文档验收

### 6.1 检查文档完整性

```powershell
# 列出所有文档
Get-ChildItem -Path . -Filter "*.md" -Recurse | Select-Object FullName
```

**应该包含以下文档**:

- ✅ `README.md`
- ✅ `VERIFICATION.md`
- ✅ `ARCHITECTURE.md`
- ✅ `DATABASE.md`
- ✅ `PRECOMMIT.md`
- ✅ `CICD.md`
- ✅ `PHASE1_SUMMARY.md`
- ✅ `PROJECT_SUMMARY.md`
- ✅ `ACCEPTANCE.md` (本文档)
- ✅ `apps/api-gateway/TESTING.md`
- ✅ `apps/web/TESTING.md`

### 6.2 检查关键配置文件

```powershell
# 检查配置文件
$files = @(
    ".pre-commit-config.yaml",
    "pyproject.toml",
    ".prettierrc",
    ".czrc",
    "docker-compose.yml",
    "docker-compose.dev.yml",
    ".github/workflows/backend.yml",
    ".github/workflows/frontend.yml",
    ".github/workflows/ci.yml"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing" -ForegroundColor Red
    }
}
```

**✅ 验收标准**: 所有文件都存在

---

## 📊 验收评分表

### 后端 (35 分)
- [ ] 代码质量检查通过 (5 分)
- [ ] 单元测试通过 (10 分)
- [ ] 集成测试通过 (5 分)
- [ ] 测试覆盖率 ≥ 70% (10 分)
- [ ] 服务启动成功 (5 分)

### 前端 (25 分)
- [ ] 代码质量检查通过 (5 分)
- [ ] 测试通过 (10 分)
- [ ] 测试覆盖率 ≥ 70% (5 分)
- [ ] 构建成功 (5 分)

### Docker (20 分)
- [ ] 所有服务启动成功 (10 分)
- [ ] 端到端功能正常 (10 分)

### Pre-commit (10 分)
- [ ] Hooks 安装成功 (5 分)
- [ ] Hooks 检查通过 (5 分)

### 文档 (10 分)
- [ ] 文档完整性 (5 分)
- [ ] 配置文件完整性 (5 分)

**总分**: 100 分
**通过标准**: ≥ 85 分

---

## 🎯 快速验收脚本

### 一键验收（PowerShell）

创建 `quick-acceptance.ps1`:

```powershell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    CxyGPT 项目验收脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$score = 0

# 1. 后端测试
Write-Host "`n[1/5] 后端测试..." -ForegroundColor Yellow
cd apps\api-gateway
if (Test-Path .venv) {
    .\.venv\Scripts\Activate.ps1
    $result = pytest --tb=short -q
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 后端测试通过" -ForegroundColor Green
        $score += 25
    }
}

# 2. 前端测试
Write-Host "`n[2/5] 前端测试..." -ForegroundColor Yellow
cd ..\..\apps\web
$result = npm run test:run
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 前端测试通过" -ForegroundColor Green
    $score += 25
}

# 3. Docker 构建
Write-Host "`n[3/5] Docker 构建..." -ForegroundColor Yellow
cd ..\..
docker-compose -f docker-compose.dev.yml build
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker 构建成功" -ForegroundColor Green
    $score += 20
}

# 4. Pre-commit 检查
Write-Host "`n[4/5] Pre-commit 检查..." -ForegroundColor Yellow
pre-commit run --all-files
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pre-commit 检查通过" -ForegroundColor Green
    $score += 20
}

# 5. 文档检查
Write-Host "`n[5/5] 文档检查..." -ForegroundColor Yellow
$docs = @("README.md", "ARCHITECTURE.md", "DATABASE.md", "PRECOMMIT.md", "CICD.md")
$docsExist = $true
foreach ($doc in $docs) {
    if (-not (Test-Path $doc)) {
        Write-Host "✗ $doc 缺失" -ForegroundColor Red
        $docsExist = $false
    }
}
if ($docsExist) {
    Write-Host "✓ 文档完整" -ForegroundColor Green
    $score += 10
}

# 最终结果
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "验收得分: $score / 100" -ForegroundColor $(if ($score -ge 85) { "Green" } else { "Red" })
Write-Host "验收状态: $(if ($score -ge 85) { "✓ 通过" } else { "✗ 未通过" })" -ForegroundColor $(if ($score -ge 85) { "Green" } else { "Red" })
Write-Host "========================================" -ForegroundColor Cyan
```

**运行验收脚本**:

```powershell
.\quick-acceptance.ps1
```

---

## 📝 验收报告模板

完成验收后，填写以下报告:

```
================================
CxyGPT 项目验收报告
================================

验收日期: _______________
验收人: _______________

一、环境检查
[ ] Python 3.11+
[ ] Node.js 20+
[ ] Docker
[ ] Git

二、后端验收 (35 分)
[ ] 代码质量检查: ___ / 5
[ ] 单元测试: ___ / 10
[ ] 集成测试: ___ / 5
[ ] 覆盖率: ___ / 10
[ ] 服务启动: ___ / 5

三、前端验收 (25 分)
[ ] 代码质量检查: ___ / 5
[ ] 测试: ___ / 10
[ ] 覆盖率: ___ / 5
[ ] 构建: ___ / 5

四、Docker 验收 (20 分)
[ ] 服务启动: ___ / 10
[ ] 端到端: ___ / 10

五、Pre-commit (10 分)
[ ] Hooks 安装: ___ / 5
[ ] Hooks 检查: ___ / 5

六、文档 (10 分)
[ ] 文档完整性: ___ / 5
[ ] 配置完整性: ___ / 5

总分: ___ / 100

验收结论: [ ] 通过  [ ] 不通过

备注:
___________________________________
___________________________________
___________________________________

签名: _______________
```

---

## 🆘 常见问题

### Q1: pytest 找不到模块

**解决方案**:
```powershell
# 确保虚拟环境激活
.\.venv\Scripts\Activate.ps1

# 重新安装
pip install -e .
```

### Q2: Docker 服务启动失败

**解决方案**:
```powershell
# 查看详细日志
docker-compose -f docker-compose.dev.yml logs

# 清理并重启
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Q3: Pre-commit hooks 失败

**解决方案**:
```powershell
# 清理缓存
pre-commit clean

# 重新安装
pre-commit install --install-hooks

# 再次运行
pre-commit run --all-files
```

---

**验收时间预计**: 50-60 分钟
**建议验收人员**: 技术负责人 + QA + 开发者

**验收完成后**: 请保存验收报告并归档
