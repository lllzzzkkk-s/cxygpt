# API Gateway for CxyGPT

FastAPI 网关，提供 OpenAI 兼容 API，支持 Admission、限流、队列、超时、单人/多人模式切换。

## 安装

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 运行

```bash
# 开发模式（Mock）
python -m api_gateway.main

# 连接真实 vLLM
# 修改 .env: USE_MOCK=0
python -m api_gateway.main
```

## API 文档

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 核心功能

- ✅ OpenAI 兼容 API (`/v1/chat/completions`, `/v1/embeddings`)
- ✅ Swagger 自动文档
- ✅ Admission（请求整形，413）
- ✅ 限流（QPS + TPM，429）
- ✅ 有界队列（503）
- ✅ 超时保护
- ✅ 客户端取消支持
- ✅ 单人/多人双模式
- ✅ 显存自适应分档
- ✅ 结构化日志（JSON）
- ✅ Mock 模式（开发测试）

## 测试

```bash
pytest
```
