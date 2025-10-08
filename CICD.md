# ================================
# CI/CD 配置指南
# ================================

## 概述

本项目使用 GitHub Actions 实现完整的 CI/CD 流水线，包括：

- ✅ 自动化测试 (后端 + 前端)
- ✅ 代码质量检查 (Linting, Formatting, Type Checking)
- ✅ 安全扫描 (Trivy)
- ✅ Docker 镜像构建和推送
- ✅ 自动化发布

---

## Workflows 说明

### 1. Backend Tests (`.github/workflows/backend.yml`)

**触发条件**:
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支
- 仅当 `apps/api-gateway/**` 变更时触发

**执行流程**:
1. **代码检查**
   - Ruff: Python linter
   - Black: 代码格式化检查
   - MyPy: 类型检查

2. **测试**
   - Pytest: 运行所有测试
   - Coverage: 生成覆盖率报告
   - 上传覆盖率到 Codecov

3. **Docker 构建**
   - 构建 API Gateway 镜像
   - 使用 GitHub Actions 缓存加速

**Matrix 策略**:
- Python 3.11, 3.12

---

### 2. Frontend Tests (`.github/workflows/frontend.yml`)

**触发条件**:
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支
- 仅当 `apps/web/**` 变更时触发

**执行流程**:
1. **代码检查**
   - ESLint: JavaScript/TypeScript linter
   - Prettier: 代码格式化检查
   - TypeScript: 类型检查

2. **测试**
   - Vitest: 运行所有测试
   - Coverage: 生成覆盖率报告
   - 上传覆盖率到 Codecov

3. **构建**
   - Vite 构建生产版本
   - 上传构建产物

4. **Docker 构建**
   - 构建 Web 镜像

**Matrix 策略**:
- Node.js 20.x, 22.x

---

### 3. Full Stack CI (`.github/workflows/ci.yml`)

**触发条件**:
- Push 到 `main` 分支
- Pull Request 到 `main` 分支

**执行流程**:
1. **Backend Tests** (复用 backend.yml)
2. **Frontend Tests** (复用 frontend.yml)
3. **Integration Tests**
   - 启动 PostgreSQL 服务
   - 启动 Redis 服务
   - 运行集成测试
4. **Security Scan**
   - Trivy 漏洞扫描
   - 上传结果到 GitHub Security
5. **Summary**
   - 汇总所有检查结果

---

### 4. Docker Build and Push (`.github/workflows/docker.yml`)

**触发条件**:
- Push 到 `main` 分支
- 创建 tag (`v*.*.*`)
- 发布 release

**执行流程**:
1. **构建镜像**
   - API Gateway 镜像
   - Web 镜像

2. **推送到 GHCR**
   - GitHub Container Registry
   - 自动生成多个 tag:
     - `main` (主分支)
     - `v1.2.3` (版本号)
     - `v1.2` (主次版本)
     - `sha-abc123` (commit SHA)

3. **创建部署产物**
   - `docker-compose.yml`
   - `infra/` 配置文件

---

### 5. Release (`.github/workflows/release.yml`)

**触发条件**:
- 创建 tag (`v*.*.*`)

**执行流程**:
1. **生成 Changelog**
   - 自动提取两个 tag 之间的提交
   - 格式化为 Markdown

2. **创建 GitHub Release**
   - 发布说明
   - Docker 镜像链接
   - 文档链接

3. **通知**
   - 发布通知

---

## 配置 Secrets

在 GitHub 仓库设置中配置以下 Secrets:

### 必需的 Secrets

1. **CODECOV_TOKEN**
   - 用途: 上传测试覆盖率
   - 获取: https://codecov.io/
   - 设置: Settings → Secrets → New repository secret

### 可选的 Secrets

2. **DOCKER_USERNAME** & **DOCKER_PASSWORD**
   - 用途: 推送到 Docker Hub (如果使用)
   - 注: GHCR 使用 GITHUB_TOKEN，无需额外配置

3. **SLACK_WEBHOOK** (自定义)
   - 用途: Slack 通知
   - 需要修改 workflow 添加通知步骤

---

## 状态徽章

在 README.md 中添加状态徽章:

```markdown
![Backend Tests](https://github.com/YOUR_USERNAME/cxygpt/workflows/Backend%20Tests/badge.svg)
![Frontend Tests](https://github.com/YOUR_USERNAME/cxygpt/workflows/Frontend%20Tests/badge.svg)
![Full Stack CI](https://github.com/YOUR_USERNAME/cxygpt/workflows/Full%20Stack%20CI/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/cxygpt/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/cxygpt)
```

---

## 本地测试 Workflows

### 使用 act 工具

```bash
# 安装 act
# Windows (使用 Chocolatey)
choco install act-cli

# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# 运行特定 workflow
act -W .github/workflows/backend.yml

# 运行所有 workflows
act
```

---

## 工作流程示例

### 场景 1: 开发新功能

```bash
# 1. 创建功能分支
git checkout -b feat/new-feature

# 2. 开发和提交
git add .
git commit -m "feat(api): add new endpoint"

# 3. 推送到远程
git push origin feat/new-feature

# 4. 创建 Pull Request
# GitHub Actions 自动运行:
# - Backend Tests (如果修改了 apps/api-gateway)
# - Frontend Tests (如果修改了 apps/web)
# - Pre-commit hooks 检查

# 5. 合并到 main
# 触发 Full Stack CI
```

### 场景 2: 发布新版本

```bash
# 1. 确保在 main 分支且代码最新
git checkout main
git pull origin main

# 2. 创建版本 tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# 3. 推送 tag
git push origin v1.0.0

# 4. GitHub Actions 自动执行:
# - Docker Build and Push
# - Create Release
# - 生成 Changelog
# - 发布 GitHub Release
```

### 场景 3: 热修复

```bash
# 1. 创建 hotfix 分支
git checkout -b hotfix/critical-bug

# 2. 修复并提交
git add .
git commit -m "fix(api): resolve critical security issue"

# 3. 推送并创建 PR
git push origin hotfix/critical-bug

# 4. 快速合并后发布
git checkout main
git merge hotfix/critical-bug
git tag -a v1.0.1 -m "Hotfix: critical security issue"
git push origin main --tags
```

---

## 优化建议

### 1. 加速构建

```yaml
# 使用缓存
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# 使用 Docker layer caching
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### 2. 并行执行

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: [3.11, 3.12]
        node-version: [20.x, 22.x]
```

### 3. 条件执行

```yaml
# 只在特定路径变更时运行
on:
  push:
    paths:
      - 'apps/api-gateway/**'
```

---

## 监控和调试

### 查看 Workflow 运行

1. 访问 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择具体的 workflow run
4. 查看每个 step 的日志

### 调试失败的 Workflow

```yaml
# 添加调试步骤
- name: Debug info
  run: |
    echo "Python version: $(python --version)"
    echo "Node version: $(node --version)"
    echo "Working directory: $(pwd)"
    ls -la
```

### 使用 tmate 进行交互式调试

```yaml
# 添加 tmate step
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
```

---

## 最佳实践

### 1. Secrets 管理
- ❌ 不要在代码中硬编码敏感信息
- ✅ 使用 GitHub Secrets
- ✅ 使用环境变量

### 2. 版本管理
- ✅ 使用语义化版本 (SemVer): `v1.2.3`
- ✅ 主版本: 不兼容的 API 变更
- ✅ 次版本: 向后兼容的新功能
- ✅ 补丁版本: 向后兼容的 Bug 修复

### 3. 提交规范
- ✅ 使用 Conventional Commits
- ✅ `feat:` 新功能
- ✅ `fix:` Bug 修复
- ✅ `docs:` 文档
- ✅ `test:` 测试

### 4. 分支策略
- `main`: 生产环境
- `develop`: 开发环境
- `feat/*`: 功能分支
- `hotfix/*`: 热修复分支

---

## 故障排除

### Q1: Codecov 上传失败

**解决方案**:
```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    fail_ci_if_error: false  # 不因上传失败而中断
```

### Q2: Docker 构建超时

**解决方案**:
- 使用 layer caching
- 减小镜像体积
- 使用 multi-stage builds

### Q3: 测试在 CI 中失败但本地通过

**可能原因**:
- 环境变量不同
- 数据库未正确初始化
- 时区问题
- 依赖版本不一致

**解决方案**:
```yaml
# 设置环境变量
env:
  TZ: UTC
  DATABASE_URL: sqlite:///test.db
```

---

## 相关资源

- **GitHub Actions 文档**: https://docs.github.com/en/actions
- **Docker Build Push Action**: https://github.com/docker/build-push-action
- **Codecov**: https://codecov.io/
- **act (本地测试)**: https://github.com/nektos/act

---

**配置时间**: 2025-10-06
**维护者**: Claude Code
