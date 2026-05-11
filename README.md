# Interview Agent - AI 模拟面试系统

> 上传简历 → 选择岗位 → AI 实时模拟面试 → 5维评估报告，助你斩获心仪 Offer

## 功能概览

| 功能 | 描述 |
|------|------|
| 📄 简历上传与解析 | 支持 PDF / Word 格式，自动提取关键信息 |
| 🏢 岗位资料管理 | 创建、编辑目标岗位信息与 JD |
| 🎯 5岗位精准出题 | 产品经理 / 运营 / 数据分析 / 算法 / 研发，按岗位定制面试题 |
| 💬 AI 实时对话 | 流式输出，模拟真实面试节奏，支持追问 |
| 🗣️ 语音面试（可选） | TTS 朗读 + STT 语音输入 |
| 📊 5维评估报告 | 岗位专属评分维度 + 雷达图 + 逐题点评 + 改进建议 |
| 📝 面试反思总结 | AI 生成总结 + 逐题笔记 + 重点标记 |
| 📁 面试历史记录 | 查看过往面试会话与报告 |

## 技术架构

```
┌──────────────────────────────────────────────┐
│                  Frontend                     │
│    Vue 3 + Vite + Vue Router + Pinia         │
│    ECharts (可视化) + Web Speech API          │
│              localhost:5173                    │
└────────────────┬─────────────────────────────┘
                 │ Vite Proxy (/api → :8000)
┌────────────────▼─────────────────────────────┐
│                  Backend                      │
│    FastAPI + SQLAlchemy + SQLite              │
│    python-dotenv + httpx                      │
│              localhost:8000                    │
├──────────────────────────────────────────────┤
│  LLM API (OpenAI 兼容格式)                    │
│  ├─ ECNU Plus / 智谱 GLM / DeepSeek / OpenAI │
│  └─ SiliconFlow BAAI/bge-m3 (嵌入, P1)       │
└──────────────────────────────────────────────┘
```

## 项目结构

```
interview-agent/
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 入口：uvicorn 启动 + 路由注册
│   ├── .env.example            # 环境变量模板（复制后填写 API Key）
│   ├── requirements.txt        # Python 依赖
│   ├── models/
│   │   └── database.py         # SQLAlchemy 数据模型 + DB 引擎
│   ├── routers/
│   │   ├── resume.py           # /api/resumes — 简历管理
│   │   ├── profile.py          # /api/profiles — 岗位资料 CRUD
│   │   ├── interview.py        # /api/sessions — 面试会话 + SSE 对话
│   │   ├── report.py           # /api/sessions/{id}/report — 评估报告
│   │   ├── question.py         # /api/questions — 面试问题查询
│   │   ├── voice.py            # /api/voice — TTS 语音合成
│   │   └── reflection.py       # /api/sessions/{id}/reflection — 反思总结
│   ├── services/
│   │   ├── llm_engine.py       # LLM API 封装（对话 + 嵌入）
│   │   ├── prompt_selector.py  # 岗位类别识别 + 评分维度/权重/Rubric
│   │   ├── scorer.py           # 加权评分计算
│   │   ├── resume_parser.py    # PDF/DOCX 文本提取
│   │   ├── state_machine.py    # 面试对话状态机（6状态）
│   │   └── rag_engine.py       # RAG 引擎（P1 占位）
│   ├── prompts/                # 10套 Prompt 模板（5岗×2轮）
│   │   ├── pm_round1.py        # 产品经理 - 业务面
│   │   ├── pm_hr.py            # 产品经理 - HR 面
│   │   ├── ops_round1.py       # 运营 - 业务面
│   │   ├── ops_hr.py           # 运营 - HR 面
│   │   ├── da_round1.py        # 数据分析 - 业务面
│   │   ├── da_hr.py            # 数据分析 - HR 面
│   │   ├── algo_round1.py      # 算法 - 业务面
│   │   ├── algo_hr.py          # 算法 - HR 面
│   │   ├── dev_round1.py       # 研发 - 业务面
│   │   ├── dev_hr.py           # 研发 - HR 面
│   │   ├── scoring.py          # 评分 Prompt
│   │   ├── resume_extraction.py # 简历结构化提取 Prompt
│   │   └── question_quality.py # 题目质量评估 Prompt
│   └── rag/                    # RAG 模块（P1 阶段，当前占位）
│       ├── embedder.py
│       ├── knowledge_base.py
│       └── retriever.py
│
├── frontend/                   # Vue 3 前端
│   ├── package.json
│   ├── vite.config.js          # Vite 配置 + API 代理
│   └── src/
│       ├── main.js             # 入口
│       ├── style.css           # 全局 Design Token 系统
│       ├── router/index.js     # 5 页面路由
│       ├── stores/             # Pinia 状态管理
│       │   ├── resume.js       # 简历 Store
│       │   ├── interview.js    # 面试会话 Store
│       │   └── application.js  # 投递 Store（占位）
│       ├── views/              # 页面组件
│       │   ├── HomePage.vue         # 首页（资料库 + 快速开始）
│       │   ├── InterviewConfig.vue  # 面试配置（4步向导）
│       │   ├── InterviewChat.vue    # 面试对话（SSE 流式）
│       │   ├── EvaluationReport.vue # 评估报告（5维 + 雷达图）
│       │   └── HistoryPage.vue      # 面试历史
│       └── components/
│           ├── AppHeader.vue        # 全局导航栏
│           ├── AppLayout.vue        # 共享布局
│           └── ReflectionModal.vue  # 反思总结弹窗
│
├── data/                       # 数据目录（不纳入 Git）
│   ├── interview_agent.db      # SQLite 数据库
│   ├── uploads/                # 上传的简历文件
│   └── knowledge_base/         # RAG 知识库（P1）
│
├── logs/                       # 运行日志
├── .gitignore
└── README.md
```

## 快速开始

### 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

### 1. 克隆项目

```bash
git clone https://github.com/your-username/interview-agent.git
cd interview-agent
```

### 2. 配置 API Key（必做）

本项目使用 OpenAI 兼容格式的 LLM API。你只需要 **一个 API Key** 即可启动核心功能。

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填写你的 API Key：

```env
# ── 必填：LLM 对话模型 ──
# 以下提供几种常见配置方案，选一种即可：

# 方案 A：ECNU Plus（华东师大内部服务）
LLM_BASE_URL=https://chat.ecnu.edu.cn/open/api/v1
LLM_API_KEY=sk-xxxxxxxxxxxxx
LLM_MODEL=ecnu-plus

# 方案 B：智谱 GLM（推荐，国内直连）
# LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
# LLM_API_KEY=xxxxxxxx.xxxxxxxx
# LLM_MODEL=glm-4-flash

# 方案 C：DeepSeek（性价比高）
# LLM_BASE_URL=https://api.deepseek.com/v1
# LLM_API_KEY=sk-xxxxxxxxxxxxx
# LLM_MODEL=deepseek-chat

# 方案 D：OpenAI（需代理）
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_API_KEY=sk-xxxxxxxxxxxxx
# LLM_MODEL=gpt-4o-mini

# ── 选填：嵌入模型（RAG 功能需要，MVP 可不填）──
# EMBEDDING_URL=https://api.siliconflow.cn/v1/embeddings
# EMBEDDING_MODEL=BAAI/bge-m3
# EMBEDDING_API_KEY=sk-xxxxxxxxxxxxx
```

> **如何获取 API Key？**
> - **智谱 GLM**：注册 [open.bigmodel.cn](https://open.bigmodel.cn)，免费额度可用
> - **DeepSeek**：注册 [platform.deepseek.com](https://platform.deepseek.com)，新用户送 Token
> - **SiliconFlow**：注册 [siliconflow.cn](https://siliconflow.cn)，免费嵌入模型额度

### 3. 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端运行在 http://localhost:8000，首次启动自动创建数据库。

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173，通过 Vite 代理转发 API 请求。

### 5. 访问应用

浏览器打开 http://localhost:5173 即可使用。

### 一键启动（Windows）

双击 `start-persistent.bat` 或在 PowerShell 中运行：

```powershell
.\start-all.ps1
```

该脚本会自动清理旧进程、启动后端和前端、健康检查并打开浏览器。

## 环境变量说明

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `LLM_BASE_URL` | ✅ | - | LLM API 基础地址（OpenAI 兼容格式，以 `/v1` 结尾） |
| `LLM_API_KEY` | ✅ | - | LLM API 密钥 |
| `LLM_MODEL` | ✅ | `ecnu-plus` | 模型名称 |
| `EMBEDDING_URL` | ❌ | SiliconFlow | 嵌入模型 API 地址（RAG 功能需要） |
| `EMBEDDING_MODEL` | ❌ | `BAAI/bge-m3` | 嵌入模型名称 |
| `EMBEDDING_API_KEY` | ❌ | - | 嵌入模型 API 密钥 |
| `DATABASE_URL` | ❌ | `sqlite:///./data/interview_agent.db` | 数据库连接字符串 |

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/resumes/upload` | 上传简历（PDF/DOCX） |
| GET | `/api/resumes` | 获取简历列表 |
| DELETE | `/api/resumes/{id}` | 删除简历 |
| POST | `/api/profiles` | 创建岗位资料 |
| GET | `/api/profiles` | 获取岗位列表 |
| PUT | `/api/profiles/{id}` | 更新岗位资料 |
| DELETE | `/api/profiles/{id}` | 删除岗位资料 |
| POST | `/api/sessions` | 创建面试会话 |
| POST | `/api/sessions/{id}/chat` | 发送消息（SSE 流式响应） |
| POST | `/api/sessions/{id}/end` | 结束面试，生成评估 |
| GET | `/api/sessions/{id}/report` | 获取评估报告 |
| POST | `/api/sessions/{id}/reflection` | 生成/保存反思总结 |
| GET | `/api/voice/tts` | 文字转语音（edge-tts） |
| GET | `/api/health` | 健康检查 |

完整 API 文档启动后访问：http://localhost:8000/docs

## 支持的面试岗位

| 岗位 | 业务面评分维度 | HR面侧重 |
|------|---------------|---------|
| 产品经理 | 产品思维(25%) / 数据能力(20%) / 项目深度(20%) / 表达逻辑(20%) / 业务理解(15%) | 职业动机、团队协作、抗压能力 |
| 运营 | 增长思维(25%) / 数据分析(20%) / 执行落地(20%) / 创意策划(20%) / 用户洞察(15%) | 加班接受度、创意与执行平衡、跨部门协作 |
| 数据分析 | SQL能力(20%) / 统计分析(20%) / 业务洞察(20%) / 模型应用(20%) / 沟通表达(20%) | 数据准确性态度、与非技术方沟通 |
| 算法 | 算法基础(20%) / 工程能力(20%) / 项目深度(25%) / 系统设计(20%) / 表达能力(15%) | 技术热情、学术与工业权衡、跨团队沟通 |
| 研发 | 代码能力(20%) / 系统设计(20%) / 技术深度(20%) / 项目经验(25%) / 协作沟通(15%) | 代码质量意识、与PM/测试协作、技术vs管理路线 |

## 面试流程

```
上传简历 → 选择岗位 → 配置轮次/风格 → AI 面试对话 → 查看评估报告 → 反思总结
```

对话状态机：

```
idle → self_intro → topic_question ⇄ follow_up → wrap_up → evaluation
```

- 业务面：最多 8 题，每题最多 3 次追问
- HR 面：最多 5 题，侧重软素质考察

## 开发指南

### 前端开发

```bash
cd frontend
npm run dev      # 开发服务器 (localhost:5173)
npm run build    # 生产构建
npm run preview  # 预览生产构建
```

前端 Design Token 系统定义在 `src/style.css`，使用 CSS 变量统一管理颜色、间距、圆角等。无外部 UI 框架依赖。

### 后端开发

```bash
cd backend
python main.py   # 开发服务器 (localhost:8000, --reload)
```

添加新岗位支持：
1. `backend/prompts/` 下新建 `{position}_round1.py` 和 `{position}_hr.py`
2. `backend/services/prompt_selector.py` 中添加关键词映射、评分维度、Rubric
3. `backend/routers/interview.py` 的 `POSITION_QUESTIONS` 字典添加题目模板

### 数据库

使用 SQLite，首次启动自动建表。数据库文件位于 `data/interview_agent.db`。

如需重置：删除 `data/interview_agent.db` 后重启后端。

## 部署说明

### 生产构建

```bash
# 前端构建
cd frontend
npm run build
# 产物在 frontend/dist/

# 后端启动（关闭 reload）
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Nginx 反向代理示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/interview-agent/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # SSE 流式接口需要关闭缓冲
    location /api/sessions/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
}
```

## 开发里程碑

- [x] **M1**：项目搭建（FastAPI + Vue3 + 数据模型 + API 骨架）
- [x] **M2**：简历解析（pdfplumber + python-docx + LLM 结构化提取）
- [x] **M3**：面试对话核心（5岗×2轮 Prompt + 状态机 + SSE 流式输出）
- [x] **M4**：评估报告（5维评分 + 雷达图 + 逐题点评 + 改进建议）
- [x] **M5**：页面串联（5 页面路由 + Pinia + Design Token 系统）
- [x] **M6**：打磨优化（语音面试 + 反思总结 + 岗位资料编辑 + UI 美化）
- [ ] **P1**：RAG 知识库增强（题库数据库 + 语义检索 + 网络爬取面经）

## License

MIT
