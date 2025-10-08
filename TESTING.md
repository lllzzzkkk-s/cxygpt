# ================================
# 测试使用指南
# ================================

## 安装测试依赖

```bash
cd apps/api-gateway

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装测试依赖
pip install -r requirements-test.txt
```

---

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/unit/test_entities.py
pytest tests/integration/test_repositories.py
```

### 运行特定测试类/函数

```bash
pytest tests/unit/test_entities.py::TestMessage
pytest tests/unit/test_entities.py::TestMessage::test_create_message
```

### 按标记运行

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 只运行数据库测试
pytest -m db

# 排除慢速测试
pytest -m "not slow"
```

---

## 测试覆盖率

### 生成覆盖率报告

```bash
# 运行测试并生成覆盖率
pytest --cov=api_gateway --cov-report=html

# 查看 HTML 报告
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS/Linux
```

### 查看未覆盖的代码

```bash
pytest --cov=api_gateway --cov-report=term-missing
```

### 覆盖率目标

- **最低要求**: 70%
- **推荐目标**: 85%
- **理想目标**: 95%

---

## 测试组织

### 目录结构

```
tests/
├── conftest.py              # 全局 fixtures
├── unit/                    # 单元测试
│   ├── test_entities.py     # 测试实体
│   ├── test_services.py     # 测试领域服务
│   └── test_use_cases.py    # 测试用例
├── integration/             # 集成测试
│   ├── test_repositories.py # 测试仓储
│   └── test_api.py          # 测试 API（待添加）
└── fixtures/                # 测试数据
```

### 测试分类

#### Unit Tests（单元测试）
- 测试单个函数/方法
- 不依赖外部服务
- 快速执行
- 使用 Mock

**示例**：
```python
@pytest.mark.unit
def test_create_message():
    message = ChatService.create_message(MessageRole.USER, "Hello")
    assert message.content == "Hello"
```

#### Integration Tests（集成测试）
- 测试多个组件协作
- 可能使用数据库
- 较慢执行

**示例**：
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_save_session(db_session):
    repo = SQLAlchemyChatSessionRepository(db_session)
    session = await repo.save(sample_session)
    assert session.id is not None
```

---

## 编写测试

### 基本结构

```python
import pytest
from api_gateway.domain.entities import Message, MessageRole


class TestMessage:
    """测试消息实体"""

    def test_create_message(self):
        """测试创建消息"""
        # Arrange（准备）
        content = "Hello"
        role = MessageRole.USER

        # Act（执行）
        message = Message(id="1", role=role, content=content, tokens=5)

        # Assert（断言）
        assert message.content == content
        assert message.role == role
```

### 使用 Fixtures

```python
def test_with_fixture(sample_user):
    """使用 fixture 的测试"""
    assert sample_user.id is not None
    assert sample_user.is_active is True
```

### 异步测试

```python
@pytest.mark.asyncio
async def test_async_function(db_session):
    """异步测试"""
    result = await some_async_function()
    assert result is not None
```

### 测试异常

```python
def test_raises_exception():
    """测试抛出异常"""
    with pytest.raises(ValueError, match="Invalid input"):
        raise ValueError("Invalid input")
```

### 使用 Mock

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_with_mock():
    """使用 Mock 的测试"""
    mock_repo = AsyncMock()
    mock_repo.save.return_value = sample_data

    result = await some_function(mock_repo)
    assert result == expected_result
    mock_repo.save.assert_called_once()
```

---

## 测试最佳实践

### 1. 测试命名

- **文件**: `test_<module_name>.py`
- **类**: `Test<ClassName>`
- **函数**: `test_<function_name>_<scenario>`

**好例子**：
```python
def test_create_message_with_valid_content()
def test_create_message_with_empty_content_raises_error()
```

### 2. AAA 模式

```python
def test_example():
    # Arrange（准备）
    user = create_user()

    # Act（执行）
    result = user.do_something()

    # Assert（断言）
    assert result == expected_value
```

### 3. 一个测试一个断言主题

**不好**：
```python
def test_user():
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.is_active is True
```

**好**：
```python
def test_user_name():
    assert user.name == "Alice"

def test_user_email():
    assert user.email == "alice@example.com"

def test_user_is_active():
    assert user.is_active is True
```

### 4. 使用有意义的断言消息

```python
assert len(messages) > 0, "Should have at least one message"
assert user.is_active, f"User {user.id} should be active"
```

### 5. 清理测试数据

```python
@pytest.fixture
async def clean_db(db_session):
    """清理数据库"""
    yield db_session
    # 清理
    await db_session.rollback()
```

---

## 持续集成

### GitHub Actions 配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-test.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## 常见问题

### Q1: 测试运行很慢

**解决方案**：
```bash
# 并行运行测试
pip install pytest-xdist
pytest -n auto

# 只运行失败的测试
pytest --lf

# 跳过慢速测试
pytest -m "not slow"
```

### Q2: 数据库测试冲突

**解决方案**：
- 每个测试使用独立的事务
- 测试后回滚
- 使用内存数据库（SQLite :memory:）

### Q3: 异步测试报错

**解决方案**：
```python
# 确保添加 pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async():
    ...

# 检查 pytest.ini 配置
# asyncio_mode = auto
```

---

## 相关资源

- **Pytest 文档**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Coverage.py**: https://coverage.readthedocs.io/

---

**当前测试覆盖率目标**: 80%
**最后更新**: 2025-10-06
