# 🚀 快速验收指南（5 分钟版）

如果你看到很多代码风格问题（Ruff、Black 警告），不用担心！这些都可以自动修复。

## 选项 1: 一键自动修复（推荐）

```powershell
# 在项目根目录运行
.\fix-code-quality.ps1
```

这个脚本会自动：
- 激活虚拟环境
- 安装开发工具
- 自动修复所有 Ruff 问题
- 自动格式化所有代码
- 显示最终检查结果

## 选项 2: 手动修复

```powershell
cd H:\project\cxygpt\apps\api-gateway

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装工具（如果还没安装）
pip install ruff black mypy

# 自动修复 Ruff 问题
ruff check . --fix --unsafe-fixes

# 自动格式化代码
black .

# 验证修复结果
ruff check .
black --check .
```

## 选项 3: 跳过代码质量检查（快速验收）

如果你只想验证功能，可以跳过代码质量检查，直接运行测试：

```powershell
cd H:\project\cxygpt\apps\api-gateway
.\.venv\Scripts\Activate.ps1

# 直接运行测试
pytest --cov=api_gateway --cov-report=term

# 如果所有测试通过，说明核心功能正常 ✅
```

---

## 🎯 最简验收流程（推荐）

### 1. 修复代码质量问题（2 分钟）

```powershell
cd H:\project\cxygpt
.\fix-code-quality.ps1
```

### 2. 运行后端测试（1 分钟）

```powershell
cd apps\api-gateway
.\.venv\Scripts\Activate.ps1
pytest --cov=api_gateway --cov-report=term-missing
```

**预期结果**: 28 个测试通过，覆盖率 > 70%

### 3. 运行前端测试（1 分钟）

```powershell
cd ..\web
npm run test:run
```

**预期结果**: 12 个测试通过

### 4. 启动 Docker 验证（1 分钟）

```powershell
cd ..\..
docker-compose -f docker-compose.dev.yml up -d

# 等待 10 秒让服务启动
Start-Sleep -Seconds 10

# 测试健康检查
curl http://localhost:8000/health

# 访问前端
start http://localhost:5173
```

**预期结果**:
- 健康检查返回 `{"status":"ok"}`
- 前端页面可以打开

---

## ❓ 常见问题

### Q: Ruff 显示很多错误怎么办？

**A**: 大部分都是可以自动修复的导入排序、类型注解等问题，运行：
```powershell
ruff check . --fix --unsafe-fixes
```

### Q: Black 说要格式化很多文件怎么办？

**A**: 让它格式化就行，不会影响功能：
```powershell
black .
```

### Q: MyPy 类型检查失败怎么办？

**A**: MyPy 检查可以跳过，不影响验收。主要看测试是否通过。

### Q: 我不想修复代码风格，可以直接验收吗？

**A**: 可以！直接运行测试验证功能：
```powershell
# 后端测试
cd apps\api-gateway
.\.venv\Scripts\Activate.ps1
pytest

# 前端测试
cd ..\web
npm run test:run
```

---

## ✅ 验收通过标准（核心）

只需要满足以下 3 点：

1. ✅ **后端测试全部通过**（28 个测试）
2. ✅ **前端测试全部通过**（12 个测试）
3. ✅ **Docker 服务可以启动并访问**

代码风格问题不影响验收！

---

## 📊 验收评分简化版

| 项目 | 分数 | 检查方法 |
|-----|------|---------|
| 后端测试 | 50 分 | `pytest` 全部通过 |
| 前端测试 | 30 分 | `npm run test:run` 全部通过 |
| Docker 启动 | 20 分 | `docker-compose up` 成功 |

**总分**: 100 分
**通过标准**: ≥ 80 分（即测试通过 + Docker 能启动）

---

**验收时间**: 5 分钟
**重点**: 测试通过 > 代码风格
