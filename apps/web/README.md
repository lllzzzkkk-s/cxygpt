# CxyGPT Web Frontend

React + TypeScript + Tailwind CSS 前端应用

## 开发

```bash
npm install
npm run dev
```

## 环境变量

创建 `.env.local` 文件：

```
VITE_API_GATEWAY_URL=http://127.0.0.1:8001
```

## 构建

```bash
npm run build
```

## 功能特性

- ✅ SSE 流式渲染
- ✅ Markdown + 代码高亮
- ✅ 会话管理（新建/重命名/删除/固定）
- ✅ 设置抽屉（temperature/top_p/max_tokens/系统提示）
- ✅ Token 估算与限额显示
- ✅ 健康检查状态灯
- ✅ 错误处理（413/429/503）
- ✅ 暗色模式
- ✅ 自动滚动

## 架构

```
src/
├── components/      # UI 组件
│   ├── TopBar.tsx
│   ├── Sidebar.tsx
│   ├── ChatPane.tsx
│   ├── ChatMessage.tsx
│   ├── ChatComposer.tsx
│   └── SettingsDrawer.tsx
├── hooks/           # 自定义 Hook
│   ├── useLimits.ts
│   ├── useHealthCheck.ts
│   └── useAutoScroll.ts
├── lib/             # 工具库
│   ├── openai.ts
│   ├── markdown.ts
│   └── tokenEstimate.ts
├── store/           # Zustand 状态管理
│   └── chat.ts
└── types/           # TypeScript 类型
    └── index.ts
```
