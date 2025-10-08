# ================================

# 前端测试指南

# ================================

## 已实现的测试

当前项目包含以下测试：

### 组件测试

- **TopBar.test.tsx** - 顶部导航栏组件测试
  - 渲染应用标题
  - 渲染菜单按钮
  - 渲染设置按钮

### 工具测试

- **openai.test.tsx** - OpenAI 客户端测试
  - 客户端创建
  - API 错误处理 (413, 429, 503)

### 类型测试

- **types/index.test.ts** - 类型定义测试
  - Message 类型
  - ChatSession 类型
  - ChatSettings 类型

---

## 安装测试依赖

测试依赖已包含在 `package.json` 中，运行：

```bash
cd apps/web
npm install
```

---

## 运行测试

### 运行所有测试（监听模式）

```bash
npm test
```

### 运行所有测试（单次运行）

```bash
npm run test:run
```

### 运行测试 UI 界面

```bash
npm run test:ui
```

在浏览器中打开 http://localhost:51204/ 查看交互式测试界面。

### 运行特定测试文件

```bash
npx vitest src/components/ChatMessage.test.tsx
```

### 运行匹配模式的测试

```bash
npx vitest --grep "ChatMessage"
```

---

## 测试覆盖率

### 生成覆盖率报告

```bash
npm run test:coverage
```

### 查看 HTML 报告

```bash
# Windows
start coverage/index.html

# macOS/Linux
open coverage/index.html
```

### 覆盖率目标

- **最低要求**: 70%
- **推荐目标**: 80%
- **理想目标**: 90%

---

## 测试组织

### 目录结构

```
src/
├── components/
│   ├── ChatMessage.tsx
│   ├── ChatMessage.test.tsx      # 组件测试
│   ├── ChatComposer.tsx
│   ├── ChatComposer.test.tsx
│   ├── Sidebar.tsx
│   ├── Sidebar.test.tsx
│   └── SettingsDrawer.test.tsx
├── hooks/
│   ├── useLimits.ts
│   ├── useLimits.test.ts         # Hook 测试
│   ├── useAutoScroll.test.ts
│   └── useHealthCheck.test.ts
└── test/
    ├── setup.ts                  # 测试配置
    └── utils.tsx                 # 测试工具函数
```

### 测试分类

#### Component Tests（组件测试）

- 测试 UI 渲染
- 测试用户交互
- 测试状态变化
- 使用 @testing-library/react

**示例**：

```tsx
import { render, screen } from '../test/utils';
import userEvent from '@testing-library/user-event';

it('renders user message correctly', () => {
  render(<ChatMessage message={mockMessage} />);
  expect(screen.getByText('Hello, world!')).toBeInTheDocument();
});

it('handles button click', async () => {
  const user = userEvent.setup();
  const onClick = vi.fn();

  render(<Button onClick={onClick}>Click me</Button>);
  await user.click(screen.getByRole('button'));

  expect(onClick).toHaveBeenCalled();
});
```

#### Hook Tests（Hook 测试）

- 测试自定义 Hook 逻辑
- 测试副作用
- 使用 renderHook

**示例**：

```tsx
import { renderHook, waitFor } from '@testing-library/react';

it('fetches data on mount', async () => {
  const { result } = renderHook(() => useLimits());

  await waitFor(() => {
    expect(result.current.limits).toBeTruthy();
  });
});
```

---

## 编写测试

### 基本组件测试结构

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../test/utils';
import userEvent from '@testing-library/user-event';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const user = userEvent.setup();
    const onAction = vi.fn();

    render(<MyComponent onAction={onAction} />);

    await user.click(screen.getByRole('button'));

    expect(onAction).toHaveBeenCalled();
  });
});
```

### 测试异步操作

```tsx
import { waitFor } from '@testing-library/react';

it('loads data asynchronously', async () => {
  render(<AsyncComponent />);

  expect(screen.getByText('Loading...')).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText('Data loaded')).toBeInTheDocument();
  });
});
```

### Mock 外部依赖

```tsx
import { vi } from 'vitest';

// Mock 模块
vi.mock('../store/chat', () => ({
  useChatStore: vi.fn(() => ({
    sessions: [],
    createSession: vi.fn(),
  })),
}));

// Mock fetch
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: async () => ({ data: 'value' }),
  } as Response)
);
```

### 测试用户输入

```tsx
import userEvent from '@testing-library/user-event';

it('handles text input', async () => {
  const user = userEvent.setup();

  render(<InputComponent />);

  const input = screen.getByRole('textbox');
  await user.type(input, 'Hello, world!');

  expect(input).toHaveValue('Hello, world!');
});
```

### 测试表单提交

```tsx
it('submits form', async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();

  render(<Form onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText(/name/i), 'John');
  await user.click(screen.getByRole('button', { name: /submit/i }));

  expect(onSubmit).toHaveBeenCalledWith({ name: 'John' });
});
```

---

## 测试最佳实践

### 1. 查询优先级

按优先级使用查询方法：

1. **getByRole** - 最推荐（可访问性）
2. **getByLabelText** - 表单元素
3. **getByPlaceholderText** - 输入框
4. **getByText** - 非交互内容
5. **getByTestId** - 最后选择

**好例子**：

```tsx
// ✅ 使用 role
screen.getByRole('button', { name: /submit/i });

// ✅ 使用 label
screen.getByLabelText(/username/i);

// ❌ 避免使用 testId（除非必要）
screen.getByTestId('submit-button');
```

### 2. 异步断言

```tsx
// ✅ 使用 waitFor
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument();
});

// ✅ 使用 findBy（内置 waitFor）
expect(await screen.findByText('Loaded')).toBeInTheDocument();

// ❌ 不要在异步操作后直接断言
expect(screen.getByText('Loaded')).toBeInTheDocument();
```

### 3. 用户交互

```tsx
// ✅ 使用 userEvent（推荐）
const user = userEvent.setup();
await user.click(button);
await user.type(input, 'text');

// ❌ 避免使用 fireEvent
fireEvent.click(button);
```

### 4. 清理和隔离

```tsx
import { beforeEach, afterEach } from 'vitest';

describe('MyComponent', () => {
  beforeEach(() => {
    // 每个测试前重置
    vi.clearAllMocks();
  });

  afterEach(() => {
    // 每个测试后清理
    vi.restoreAllMocks();
  });
});
```

### 5. 测试命名

```tsx
// ✅ 描述行为
it('shows error message when form is invalid', () => {});
it('disables submit button while loading', () => {});

// ❌ 过于技术化
it('sets state.error to true', () => {});
it('calls useEffect', () => {});
```

### 6. 避免实现细节

```tsx
// ✅ 测试行为
expect(screen.getByText('5 items')).toBeInTheDocument();

// ❌ 测试实现
expect(component.state.count).toBe(5);
```

---

## 常见场景

### 测试 Zustand Store

```tsx
import { useChatStore } from '../store/chat';

vi.mock('../store/chat', () => ({
  useChatStore: vi.fn(),
}));

it('uses store data', () => {
  vi.mocked(useChatStore).mockReturnValue({
    sessions: mockSessions,
    createSession: vi.fn(),
  } as any);

  render(<Component />);

  expect(screen.getByText('Session 1')).toBeInTheDocument();
});
```

### 测试路由导航

```tsx
// 如果使用 React Router
import { MemoryRouter } from 'react-router-dom';

render(
  <MemoryRouter initialEntries={['/chat/123']}>
    <Component />
  </MemoryRouter>
);
```

### 测试错误边界

```tsx
it('handles errors gracefully', () => {
  const consoleSpy = vi.spyOn(console, 'error').mockImplementation();

  render(
    <ErrorBoundary>
      <ThrowingComponent />
    </ErrorBoundary>
  );

  expect(screen.getByText(/error occurred/i)).toBeInTheDocument();

  consoleSpy.mockRestore();
});
```

### 测试定时器

```tsx
import { vi } from 'vitest';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

it('polls every 30 seconds', async () => {
  const { result } = renderHook(() => useHealthCheck());

  expect(fetch).toHaveBeenCalledTimes(1);

  vi.advanceTimersByTime(30000);

  await waitFor(() => {
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
```

---

## 调试测试

### 查看渲染的 DOM

```tsx
import { screen } from '@testing-library/react';

// 打印整个 DOM
screen.debug();

// 打印特定元素
screen.debug(screen.getByRole('button'));
```

### 查看可访问性树

```tsx
import { logRoles } from '@testing-library/react';

const { container } = render(<Component />);
logRoles(container);
```

### 使用 screen.logTestingPlaygroundURL

```tsx
screen.logTestingPlaygroundURL();
// 在浏览器中打开链接，可视化查询选择器
```

---

## 持续集成

### GitHub Actions 配置示例

```yaml
name: Frontend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:run
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

---

## 常见问题

### Q1: "Cannot find module" 错误

**解决方案**：

- 检查 `vite.config.ts` 中的路径别名配置
- 确保 `tsconfig.json` 中的 paths 配置一致

### Q2: "ReferenceError: fetch is not defined"

**解决方案**：

```tsx
// 在测试文件中 mock fetch
global.fetch = vi.fn();
```

### Q3: 测试超时

**解决方案**：

```tsx
// 增加超时时间
it('long running test', async () => {
  // ...
}, 10000); // 10 seconds
```

### Q4: "act" 警告

**解决方案**：

- 使用 `await` 处理异步操作
- 使用 `waitFor` 等待状态更新
- 使用 `userEvent` 代替 `fireEvent`

---

## 相关资源

- **Vitest 文档**: https://vitest.dev/
- **Testing Library**: https://testing-library.com/react
- **Testing Library Cheatsheet**: https://testing-library.com/docs/react-testing-library/cheatsheet
- **Common Mistakes**: https://kentcdodds.com/blog/common-mistakes-with-react-testing-library

---

**当前测试覆盖率目标**: 70%
**最后更新**: 2025-10-06
