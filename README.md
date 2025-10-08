# CxyGPT - 本地大模型完整工程

基于 **React + FastAPI + Django + vLLM** 的本地大模型对话系统，支持单人/多人双模式、显存自适应分档、并发控制与降级策略。

## 📋 功能特性

- **🎨 高级会话 UI**：React + TypeScript + Tailwind，SSE 流式渲染，设置抽屉，虚拟化列表
- **⚡ FastAPI 网关**：OpenAI 兼容 API，Swagger 文档，Admission/限流/队列/超时/取消
- **🔄 双模式切换**：单人家用（质量优先）⇆ 多人并发（吞吐优先）
- **📊 显存自适应**：自动检测显存并匹配配置档位（32G/48G/80G/多卡）
- **🛡️ 并发控制**：有界队列、QPS/TPM 限流、超时保护、自动降级
- **📈 可观测性**：结构化日志、指标统计、压测工具

## 🚀 快速开始

### 前置要求

- **硬件**：RTX 5090 32GB（或更高）
- **软件**：
  - Python 3.10+
  - Node.js 18+
  - CUDA 12.1+

### 三步跑通

#### 1. 启动前端（Mock 模式）

```powershell
# 安装依赖
cd apps\web
npm install

# 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

#### 2. 启动网关（Mock 模式）

```powershell
# 安装依赖
cd apps\api-gateway
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 使用单人模式配置
copy ..\..\env.single .env

# Mock 模式启动（无需 vLLM）
python -m api_gateway.main
# 访问 Swagger: http://localhost:8001/docs
```

#### 3. 切换到真实 vLLM

```powershell
# 修改 .env
USE_MOCK=0

# 启动 vLLM（根据档位选择命令）
# 详见下方 "vLLM 启动命令"
```

### vLLM 启动命令

#### 单人模式（SINGLE_32G - 全精度 bfloat16）

```bash
python -m vllm.entrypoints.openai.api_server \
  --model ~/models/Qwen3-14B \
  --served-model-name qwen3-14b \
  --dtype bfloat16 \
  --kv-cache-dtype fp8 \
  --max-model-len 3072 \
  --gpu-memory-utilization 0.95 \
  --host 0.0.0.0 \
  --port 8000
```

#### 多人模式（DEV_32G - 4bit 量化）

```bash
python -m vllm.entrypoints.openai.api_server \
  --model ~/models/Qwen3-14B-GPTQ-Int4 \
  --served-model-name qwen3-14b \
  --dtype auto \
  --kv-cache-dtype fp8 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.92 \
  --swap-space 16 \
  --host 0.0.0.0 \
  --port 8000
```

#### 服务器模式（SRV_48G/80G）

```bash
# 48GB
python -m vllm.entrypoints.openai.api_server \
  --model ~/models/Qwen3-14B \
  --served-model-name qwen3-14b \
  --dtype bfloat16 \
  --kv-cache-dtype fp8 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.92 \
  --host 0.0.0.0 \
  --port 8000

# 80GB
python -m vllm.entrypoints.openai.api_server \
  --model ~/models/Qwen3-14B \
  --served-model-name qwen3-14b \
  --dtype bfloat16 \
  --kv-cache-dtype fp8 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.92 \
  --swap-space 32 \
  --host 0.0.0.0 \
  --port 8000
```

## 🎛️ 单人 ⇆ 多人模式切换

### 方式 1：切换配置文件

```powershell
# 单人模式
cd apps\api-gateway
copy ..\..\env.single .env

# 多人模式
copy ..\..\env.multi .env
```

### 方式 2：环境变量

```powershell
# 单人模式
$env:SINGLE_USER=1

# 多人模式
$env:SINGLE_USER=0
```

### 方式 3：强制档位

```powershell
$env:FORCE_PROFILE="DEV_32G"
```

### 验证当前配置

```powershell
# 查询限额接口
curl http://localhost:8001/v1/limits

# 输出示例（单人模式）
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

## 📊 显存分档说明

| 档位 | 显存 | 模式 | max_model_len | 量化 | 特点 |
|------|------|------|---------------|------|------|
| **SINGLE_32G** | 32GB | 单人 | 3072 | bfloat16 | 质量优先，无限流 |
| **DEV_32G** | 32GB | 多人 | 4096 | 4bit | 并发模拟，限流保护 |
| **SRV_48G** | 48GB | 多人 | 8192 | bfloat16 | 更长上下文 |
| **SRV_80G** | 80GB | 多人 | 16384 | bfloat16 | 超长上下文 |
| **SRV_MULTI_80G** | 160GB+ | 多人 | 16384 | bfloat16 | 张量并行（2卡+） |

查看当前档位与建议命令：

```powershell
cd apps\api-gateway
python -m api_gateway.print_profile
```

## 🔧 项目结构

```
cxygpt/
├── apps/
│   ├── web/                # React 前端（高级会话 UI）
│   │   ├── src/
│   │   │   ├── components/ # ChatMessage, Composer, Sidebar, etc.
│   │   │   ├── hooks/      # useSSE, useLimits, useAutoScroll
│   │   │   ├── store/      # Zustand 状态管理
│   │   │   └── lib/        # openai, markdown, tokenEstimate
│   │   └── package.json
│   └── api-gateway/        # FastAPI 网关
│       ├── api_gateway/
│       │   ├── main.py     # 主应用
│       │   ├── routes/     # 路由：chat, system
│       │   ├── middleware/ # Admission, 限流, 队列
│       │   └── utils/      # 日志, 配置加载
│       └── requirements.txt
├── services/
│   └── admin/              # Django 管理后台（后续）
├── configs/
│   └── profiles.yaml       # 显存分档配置
├── scripts/
│   └── bench.py            # 并发压测脚本
├── .env.example
├── .env.single
├── .env.multi
└── README.md
```

## 🛠️ API 文档

启动网关后访问：

- **Swagger UI**：http://localhost:8001/docs
- **ReDoc**：http://localhost:8001/redoc

### 核心接口

#### 1. `/healthz` - 健康检查

```bash
curl http://localhost:8001/healthz
# => {"ok": true}
```

#### 2. `/v1/limits` - 获取当前限额

```bash
curl http://localhost:8001/v1/limits
```

响应：

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

#### 3. `/v1/chat/completions` - 对话接口

**非流式**（Swagger 可直接测试）：

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-14b",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": false,
    "max_tokens": 100
  }'
```

**流式（SSE）**：

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-14b",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": true
  }'
```

## ⚠️ 错误码说明

| 状态码 | 含义 | 操作建议 |
|--------|------|----------|
| **413** | 输入过长 | 缩短输入内容或使用更高档位 |
| **429** | 请求过多 | 稍后重试（见 `Retry-After` 头） |
| **503** | 队列已满/系统忙 | 改用短问答或稍后重试 |

前端会自动识别这些错误并显示友好提示。

## 📈 压测与观测

### 并发压测

```powershell
cd scripts
python bench.py --concurrency 50 --rounds 100 --url http://127.0.0.1:8001/v1/chat/completions
```

输出：

- 平均/P95 首 token 延迟
- 平均/P95 总耗时
- 错误率（413/429/503）
- 吞吐量（RPS）

### 查看日志

```powershell
cd apps\api-gateway
# 日志会输出到控制台，格式为结构化 JSON
# 包含：request_id, queue_time, upstream_time, tokens, degraded 等字段
```

### 指标接口（可选）

```bash
curl http://localhost:8001/metrics
# Prometheus 格式指标（如已启用）
```

## 🔄 降级策略

当 **P95 首 token 延迟** 或 **队列长度** 持续超阈值时（多人模式），自动触发降级：

1. `MAX_OUTPUT_TOKENS` 从 256 降至 128
2. 禁用"长文分析"入口（前端 UI 灰显）
3. 收紧 `temperature`/`top_p`（可选）
4. 路由长文请求到更小模型（如 7B，后续实现）

手动开关：

```powershell
# .env
AUTO_DEGRADE=1
```

## 🎯 后续规划

- [ ] Django 管理后台（用户/会话/消息/文档管理）
- [ ] RAG 集成（向量召回、重排、摘要）
- [ ] 多轮对话窗口管理与摘要回写
- [ ] 会话亲和路由（多卡场景）
- [ ] 前端历史会话加载（接入 Django DRF API）
- [ ] Nginx 反代与负载均衡

## 📝 开发指南

### 前端开发

```powershell
cd apps\web
npm run dev        # 开发服务器
npm run build      # 生产构建
npm run lint       # ESLint 检查
npm run format     # Prettier 格式化
```

### 网关开发

```powershell
cd apps\api-gateway
pip install -r requirements-dev.txt
pytest             # 运行测试
ruff check .       # 代码检查
black .            # 格式化
```

### Pre-commit Hook

```powershell
pip install pre-commit
pre-commit install
# 每次 commit 前自动运行 ruff/black/eslint/prettier
```

## 📄 许可证

MIT

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**当前状态**：✅ 任务 A（仓库初始化）已完成，正在进行任务 B（前端开发）

**最后更新**：2025-10-06
