# ================================
# Pre-commit Hooks 使用指南
# ================================

## 安装和配置

### 1. 安装 Python 依赖

```bash
cd apps/api-gateway

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # macOS/Linux

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 2. 安装 Pre-commit Hooks

```bash
# 在项目根目录
cd H:\project\cxygpt

# 安装 git hooks
pre-commit install

# 安装 commit-msg hook (用于 commitizen)
pre-commit install --hook-type commit-msg
```

### 3. 验证安装

```bash
# 对所有文件运行一次检查
pre-commit run --all-files
```

---

## Hooks 说明

### Python 相关

#### Black (代码格式化)
- **作用**: 自动格式化 Python 代码
- **配置**: `pyproject.toml` → `[tool.black]`
- **手动运行**: `black apps/api-gateway/`

#### Ruff (代码检查和格式化)
- **作用**: 快速的 Python linter，替代 flake8, isort 等
- **配置**: `pyproject.toml` → `[tool.ruff]`
- **手动运行**: `ruff check apps/api-gateway/ --fix`

#### MyPy (类型检查)
- **作用**: 静态类型检查
- **配置**: `pyproject.toml` → `[tool.mypy]`
- **手动运行**: `mypy apps/api-gateway/`

---

### JavaScript/TypeScript 相关

#### Prettier (代码格式化)
- **作用**: 格式化 JS/TS/JSON/Markdown 等
- **配置**: `.prettierrc`
- **忽略文件**: `.prettierignore`
- **手动运行**:
  ```bash
  cd apps/web
  npx prettier --write .
  ```

#### ESLint (代码检查)
- **作用**: JavaScript/TypeScript 代码质量检查
- **配置**: `apps/web/eslint.config.js`
- **手动运行**:
  ```bash
  cd apps/web
  npm run lint
  ```

---

### 通用检查

#### Pre-commit-hooks (通用检查)
- `trailing-whitespace`: 移除行尾空格
- `end-of-file-fixer`: 确保文件以换行符结尾
- `check-yaml`: 检查 YAML 语法
- `check-json`: 检查 JSON 语法
- `check-toml`: 检查 TOML 语法
- `check-added-large-files`: 防止添加大文件 (>1MB)
- `check-merge-conflict`: 检查合并冲突标记
- `detect-private-key`: 检测私钥泄露

#### Commitizen (提交信息规范)
- **作用**: 强制使用规范的提交信息
- **配置**: `.czrc`
- **提交格式**:
  ```
  <type>(<scope>): <subject>

  <body>

  <footer>
  ```

**Type 类型**:
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `build`: 构建系统
- `ci`: CI 配置
- `chore`: 其他杂项

**示例**:
```bash
git commit -m "feat(api): add chat completion endpoint"
git commit -m "fix(web): resolve infinite scroll issue"
git commit -m "docs: update README with setup instructions"
```

#### Detect-secrets (密钥扫描)
- **作用**: 防止提交敏感信息 (API keys, passwords 等)
- **配置**: `.secrets.baseline`

---

## 使用场景

### 场景 1: 正常提交代码

```bash
# 1. 添加文件
git add .

# 2. 提交 (hooks 会自动运行)
git commit -m "feat(api): add new feature"

# 如果 hooks 失败，会显示错误并阻止提交
# 修复错误后重新提交
```

### 场景 2: 跳过 Hooks (不推荐)

```bash
# 仅在紧急情况下使用
git commit -m "emergency fix" --no-verify
```

### 场景 3: 手动运行特定 Hook

```bash
# 只运行 black
pre-commit run black --all-files

# 只运行 ruff
pre-commit run ruff --all-files

# 只运行 prettier
pre-commit run prettier --all-files
```

### 场景 4: 更新 Hooks

```bash
# 更新 hooks 到最新版本
pre-commit autoupdate

# 清理缓存
pre-commit clean

# 重新安装
pre-commit install --install-hooks
```

---

## 配置文件说明

### .pre-commit-config.yaml
主配置文件，定义所有 hooks。

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
```

### pyproject.toml
Python 工具配置 (black, ruff, mypy, pytest)。

```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
```

### .prettierrc
Prettier 配置。

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2
}
```

### .czrc
Commitizen 配置，定义提交信息规范。

---

## 故障排除

### Q1: Pre-commit 安装失败

```bash
# 确保使用 Python 3.11+
python --version

# 重新安装
pip install --upgrade pre-commit
```

### Q2: Hooks 运行很慢

```bash
# 只对暂存文件运行
git add specific_file.py
git commit

# 不要使用 --all-files (除非必要)
```

### Q3: 某个 Hook 一直失败

```bash
# 查看详细错误
pre-commit run <hook-id> --verbose

# 临时禁用某个 hook
# 编辑 .pre-commit-config.yaml，在对应 hook 下添加:
# stages: [manual]
```

### Q4: 与 IDE 格式化冲突

**解决方案**:
1. 配置 IDE 使用相同的配置文件
   - VSCode: 安装 Black, Ruff, Prettier 扩展
   - PyCharm: 配置 External Tools
2. 或者禁用 IDE 的自动格式化，只依赖 pre-commit

---

## IDE 集成

### Visual Studio Code

**安装扩展**:
- Python: `ms-python.python`
- Black Formatter: `ms-python.black-formatter`
- Ruff: `charliermarsh.ruff`
- Prettier: `esbenp.prettier-vscode`
- ESLint: `dbaeumer.vscode-eslint`

**配置** (`.vscode/settings.json`):
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### PyCharm / WebStorm

1. **Settings** → **Tools** → **External Tools**
2. 添加 Black, Ruff 等工具
3. **Settings** → **Editor** → **Code Style** → 导入配置

---

## 最佳实践

### 1. 提交前运行测试

虽然 pre-commit 不会自动运行测试（太慢），但建议：

```bash
# 后端测试
cd apps/api-gateway
pytest

# 前端测试
cd apps/web
npm run test:run
```

### 2. 小步提交

- ✅ 每个功能一个提交
- ✅ 提交信息清晰描述变更
- ❌ 不要一次性提交几百个文件

### 3. 代码审查

在 Pull Request 中:
- 确保所有 hooks 通过
- 检查代码覆盖率
- 运行完整测试套件

### 4. 团队协作

- 确保团队成员都安装了 pre-commit
- 统一配置文件版本
- 定期更新 hooks

---

## 示例工作流

```bash
# 1. 开始新功能
git checkout -b feat/new-feature

# 2. 编写代码
# ... 修改文件 ...

# 3. 运行格式化（可选，pre-commit 会自动做）
black apps/api-gateway/
prettier --write apps/web/

# 4. 运行测试
pytest apps/api-gateway/tests/
npm --prefix apps/web run test:run

# 5. 暂存变更
git add .

# 6. 提交（hooks 自动运行）
git commit -m "feat(api): add new chat endpoint"

# 7. 如果 hooks 失败，修复后重新提交
# ... 修复问题 ...
git add .
git commit -m "feat(api): add new chat endpoint"

# 8. 推送
git push origin feat/new-feature
```

---

**配置时间**: 2025-10-06
**维护者**: Claude Code
