# ========================
# CxyGPT 快速验收指南
# ========================

## 前置检查

确保已安装：
- Node.js 18+
- Python 3.10+
- PowerShell（Windows）

---

## Step 1: 启动 API 网关（Mock 模式）

### 1.1 打开第一个 PowerShell 终端

```powershell
# 进入网关目录
cd H:\project\cxygpt\apps\api-gateway

# 复制单人模式配置
copy ..\..\env.single .env

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 启动网关
python -m api_gateway.main
```

**预期输出**：
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
{"timestamp":"2025-10-06T...","level":"INFO","logger":"__main__","message":"Starting CxyGPT API Gateway",...}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

**验收点**：
- ✅ 服务启动成功，监听 8001 端口
- ✅ 访问 http://localhost:8001/docs 可以看到 Swagger 文档

---

## Step 2: 测试 API 网关

### 2.1 打开浏览器访问 Swagger

URL: **http://localhost:8001/docs**

### 2.2 测试接口

#### Test 1: 健康检查
- 展开 **GET /healthz**
- 点击 "Try it out"
- 点击 "Execute"
- **预期响应**: `{"ok": true}`

#### Test 2: 获取限额
- 展开 **GET /v1/limits**
- 点击 "Try it out"
- 点击 "Execute"
- **预期响应**:
```json
{
  "max_input_tokens": 3072,
  "max_output_tokens": 512,
  "rate_qps": 0,
  "rate_tpm": 0,
  "queue_size": 1,
  "single_user": true,
  "profile": "SINGLE_32G"
}
```

#### Test 3: 聊天（非流式）
- 展开 **POST /v1/chat/completions**
- 点击 "Try it out"
- 使用以下请求体：
```json
{
  "model": "qwen3-14b",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "stream": false,
  "max_tokens": 50
}
```
- 点击 "Execute"
- **预期响应**: Mock 消息 "你好！我是一个 AI 助手。"

**验收点**：
- ✅ 所有接口返回正确
- ✅ Mock 模式下可以正常返回消息

---

## Step 3: 启动前端

### 3.1 打开第二个 PowerShell 终端

```powershell
# 进入前端目录
cd H:\project\cxygpt\apps\web

# 确保依赖已安装
npm install

# 启动开发服务器
npm run dev
```

**预期输出**：
```
VITE v7.1.9  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**验收点**：
- ✅ 服务启动成功
- ✅ 监听 5173 端口（或其他可用端口）

---

## Step 4: 前端功能验收

### 4.1 打开浏览器

URL: **http://localhost:5173**

### 4.2 界面检查

**顶栏（TopBar）**：
- ✅ 左侧显示 "CxyGPT" 品牌名
- ✅ 品牌名旁有一个绿色圆点（状态灯，表示网关健康）
- ✅ 右侧有设置图标和主题切换按钮

**左侧栏（Sidebar）**：
- ✅ 顶部有 "新对话" 按钮
- ✅ 显示一个自动创建的会话（如 "新对话 10/6 17:30"）
- ✅ 会话下方显示时间和 token 数

**中央区域（ChatPane）**：
- ✅ 中间显示欢迎信息或 "开始新对话" 提示
- ✅ 底部有输入框
- ✅ 输入框下方显示 Token 估算（如 "0 / 3072 tokens"）
- ✅ 显示 "单人模式 · SINGLE_32G"

### 4.3 发送消息测试

1. **在输入框输入**："你好"
2. **点击发送按钮**（或按 Enter）

**预期行为**：
- ✅ 用户消息立即显示在聊天区
- ✅ AI 消息逐字显示（打字效果）："你好！我是一个 AI 助手。"
- ✅ 消息气泡有头像、时间戳
- ✅ 鼠标悬停在消息上显示复制按钮

### 4.4 设置抽屉测试

1. **点击顶栏右侧的设置图标**

**预期行为**：
- ✅ 右侧弹出设置抽屉
- ✅ 显示当前档位信息：
  ```
  当前档位
  模式：单人模式
  档位：SINGLE_32G
  输入限制：3072 tokens
  输出限制：512 tokens
  ```
- ✅ 可以调整 Temperature 滑块（0-2）
- ✅ 可以调整 Top P 滑块（0-1）
- ✅ 可以调整 Max Tokens 滑块（64-512）
- ✅ 可以选择系统提示模板（默认/简洁回答/结构化 JSON 等）

2. **调整 Temperature 为 0.5，关闭抽屉**
3. **再次打开设置抽屉**

**预期行为**：
- ✅ Temperature 值保持为 0.5（持久化成功）

### 4.5 会话管理测试

1. **点击左侧 "新对话" 按钮**

**预期行为**：
- ✅ 创建新会话并切换到该会话
- ✅ 聊天区清空
- ✅ 侧边栏显示两个会话

2. **在第一个会话上右键或悬停**

**预期行为**：
- ✅ 显示操作按钮：固定、重命名、删除

3. **点击重命名**，输入 "测试会话"

**预期行为**：
- ✅ 会话名称更新为 "测试会话"

### 4.6 SSE 流式测试

1. **在输入框输入**："请用100字介绍一下人工智能"
2. **点击发送**

**预期行为**：
- ✅ AI 消息逐字显示（流式渲染）
- ✅ 发送按钮变为红色停止按钮
- ✅ 点击停止按钮可以中断生成
- ✅ 生成完成后按钮恢复为发送按钮

### 4.7 错误处理测试

1. **关闭网关**（在网关终端按 Ctrl+C）
2. **在前端发送消息**

**预期行为**：
- ✅ 顶栏状态灯变红
- ✅ 消息显示错误："网络错误，请检查网关是否启动"

3. **重新启动网关**

**预期行为**：
- ✅ 10秒内状态灯变回绿色

---

## Step 5: 模式切换测试

### 5.1 切换到多人模式

在网关终端：
1. **按 Ctrl+C 停止网关**
2. **切换配置**：
```powershell
copy ..\..\env.multi .env
```
3. **重新启动网关**：
```powershell
python -m api_gateway.main
```

### 5.2 前端验证

1. **刷新前端页面**（F5）
2. **检查输入框下方**

**预期显示**：
- ✅ "多人模式 · DEV_32G"
- ✅ Token 限制变为 "0 / 2048 tokens"

3. **打开设置抽屉**

**预期显示**：
- ✅ 输入限制：2048 tokens
- ✅ 输出限制：256 tokens
- ✅ QPS 限制：2
- ✅ TPM 限制：4000

---

## Step 6: 档位信息查看

在网关终端（新开一个终端，不要关闭运行的网关）：

```powershell
cd H:\project\cxygpt\apps\api-gateway
.\venv\Scripts\Activate.ps1
python -m api_gateway.print_profile
```

**预期输出**：
```
============================================================
CxyGPT 当前配置档位
============================================================

检测到显存: 32GB
当前档位: DEV_32G
模式: 多人并发

------------------------------------------------------------
网关配置:
------------------------------------------------------------
  MAX_INPUT_TOKENS: 2048
  MAX_OUTPUT_TOKENS: 256
  RATE_QPS: 2
  ...

------------------------------------------------------------
vLLM 配置:
------------------------------------------------------------
  dtype: auto
  kv_cache_dtype: fp8
  ...

------------------------------------------------------------
建议的 vLLM 启动命令:
------------------------------------------------------------

python -m vllm.entrypoints.openai.api_server \
  --model ~/models/Qwen3-14B \
  ...
```

---

## Step 7: 压测工具（可选）

```powershell
# 新开终端
cd H:\project\cxygpt

# 安装 httpx
pip install httpx

# 运行压测
python scripts\bench.py --concurrency 5 --rounds 5
```

**预期输出**：
```
开始压测:
  URL: http://127.0.0.1:8001/v1/chat/completions
  并发数: 5
  轮次: 5
  总请求数: 25

轮次 1/5...
...

============================================================
压测结果
============================================================

总请求数: 25
成功数: 25
失败数: 0

首 token 延迟:
  平均: 0.xxx s
  P95: 0.xxx s
  ...
```

---

## 验收清单总结

### ✅ 网关（API Gateway）
- [ ] 启动成功，监听 8001 端口
- [ ] Swagger 文档可访问（/docs）
- [ ] GET /healthz 返回 {"ok": true}
- [ ] GET /v1/limits 返回正确限额
- [ ] POST /v1/chat/completions（stream=false）返回 Mock 消息
- [ ] 单人/多人模式切换生效

### ✅ 前端（Web）
- [ ] 启动成功，可访问
- [ ] 顶栏显示品牌、状态灯、设置
- [ ] 侧边栏显示会话列表
- [ ] 自动创建首个会话
- [ ] 输入框显示 Token 估算和档位
- [ ] SSE 流式渲染（逐字显示）
- [ ] 消息支持 Markdown 渲染
- [ ] 消息可复制
- [ ] 设置抽屉正常工作
- [ ] 会话管理（新建/重命名/删除）
- [ ] 健康检查状态灯（绿/红）
- [ ] 错误提示（网关断开时）
- [ ] 模式切换后限额更新

### ✅ 工具
- [ ] print_profile 打印档位信息
- [ ] bench.py 压测工具运行

---

## 常见问题

### Q1: 前端显示空白？
**检查**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 是否有错误
3. 确认网关已启动（状态灯应为绿色）

### Q2: 状态灯一直灰色？
**原因**：网关未启动或端口不对

**解决**：
1. 确认网关运行在 8001 端口
2. 检查前端环境变量 `VITE_API_GATEWAY_URL`

### Q3: Mock 消息没有逐字显示？
**检查**：
1. 网关日志是否显示请求
2. 浏览器 Network 标签查看 SSE 请求

---

## 下一步

验收通过后，可以：
1. **接入真实 vLLM**：修改 `.env` 设置 `USE_MOCK=0`，启动 vLLM
2. **测试真实对话**：与本地大模型对话
3. **压测调优**：运行 bench.py 获取性能基准

---

**文档版本**：v1.0
**最后更新**：2025-10-06
