# AI 功能后端开发文档（FastAPI · LMS 项目）

## 0. 范围说明（Scope）

本后端仅负责学习管理系统（LMS）的 **AI 功能模块**，包含三大能力：

1. **文本文档生成大纲（Markdown）**：前端上传 md 文件，fastapi 后端将文件生成三层次 md 文档。
2. **RAG 问答（Qdrant 持久化）**：基于 LlamaIndex（双 ChatEngine：`condense_question` 与 `simple`），结合 Qdrant 向量数据库进行数据持久化与检索增强问答。
3. **GraphRAG 生成知识图谱（导出 Parquet）**：后端接受 txt，调用 ms-graphrag 的 Python 包构建与导出 Parquet 文件。

---

## 1. 目录结构（FastAPI 分层）

```
ai-backend/
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ logging.py
│  │  └─ deps.py
│  ├─ api/
│  │  └─ v1/
│  │     ├─ outline.py
│  │     ├─ rag.py
│  │     └─ graphrag.py
│  ├─ schemas/
│  │  ├─ outline.py
│  │  ├─ rag.py
│  │  └─ graphrag.py
│  ├─ services/
│  │  ├─ outline_service.py
│  │  ├─ rag_service.py
│  │  └─ graphrag_service.py
│  ├─ repositories/
│  │  └─ storage.py
│  ├─ workers/
│  │  └─ background.py
│  ├─ utils/
│  │  ├─ fileio.py
│  │  ├─ idgen.py
│  │  └─ timers.py
│  └─ constants/
│     └─ paths.py
├─ data/
│  ├─ uploads/
│  ├─ outputs/
│  │  ├─ outlines/
│  │  ├─ graphrag/
│  │  └─ rag/
│  └─ tmp/
├─ scripts/
│  ├─ build_index.py
│  └─ graphrag_runner.py
├─ tests/
│  ├─ test_outline.py
│  ├─ test_rag.py
│  └─ test_graphrag.py
├─ .env.example
├─ requirements.txt
├─ requirements-optional.txt
├─ README.md
└─ pyproject.toml
```

---

## 2. 运行环境与依赖

### Python 版本

**3.11**（兼容 FastAPI、LlamaIndex 0.13.0、qdrant-client 1.15.1 与 ms-graphrag 2.x）

### requirements.txt

```
# Web & Schema
fastapi==0.116.1
uvicorn[standard]==0.30.6
starlette==0.47.2
pydantic==2.8.2
pydantic-settings==2.4.0
aiofiles==24.1.0
orjson==3.10.7
httpx==0.27.2
loguru==0.7.2
python-dotenv==1.0.1

# OpenAI
openai==1.99.9

# LlamaIndex + Qdrant 持久化
llama-index==0.13.0
llama-index-llms-openai>=0.3.0,<0.4
llama-index-embeddings-openai>=0.3.0,<0.4
llama-index-retrievers-bm25>=0.2.0,<0.3
qdrant-client==1.15.1
llama-index-vector-stores-qdrant>=0.3.0,<0.4

# GraphRAG
graphrag==2.4.0

# 数据处理
pandas==2.2.2
pyarrow==17.0.0
```

### 环境变量（.env.example）

```
API_KEY = "sk-5LLuQ7Zk9SdvMbKAigi2fZFO27jdCZRmrxxPX85jX11sFywg"
BASE_URL = "https://api.openai-proxy.org"
RAG_EMBED_MODEL=text-embedding-3-small
RAG_LLM_MODEL=gpt-4o-mini
GRAPH_RAG_WORKDIR=./data/outputs/graphrag
QDRANT_URL=http://localhost:6333
```

---

## 3. 功能模块设计

### 3.1 文本生成大纲（Markdown）

- **输入**：md 文件
- **处理**：OpenAI 调用（基于 Notebook 提示词），输出 Markdown 大纲，使用的提示词和代码在 D:\rwai_fastapi\final_md2mindmap.ipynb。
- **输出**：Markdown 字符串 & 文件路径
- **存储**：`data/uploads/` & `data/outputs/outlines/`

### 3.2 RAG 问答（Qdrant 持久化）

- **参考代码**：问答流程、提示词等都如 D:\rwai_fastapi\LlamaIndex_ChatEngines_SharedMemory_Tutorial.ipynb 代码所示。这个 ipynb 的代码已经成功运行。但是要注意，ipynb 中用的 qdrant 是内存模式，但是我们的 fastapi 项目用 qdrant 来进行文本块相关数据的持久化。
- **索引建立**：前端会传入 md 文件， 分块后写入 Qdrant 向量库。每一个文本块会携带 course_id、course_material_id，course_material_name
- **检索问答**：支持 `condense_question` / `simple` 模式
- **共享记忆**：`用ChatSummaryMemoryBuffer` 来保存聊天的记忆，但是 ChatSummaryMemoryBuffer 的具体数据历史聊天是持久化在访问前端的用户的浏览器的 localStorage。前端发出来的请求会选择聊天的模式是 condense_question 还是 simple.

### 3.3 GraphRAG（txt → Parquet）

- **输入**：md 文件
- **处理**：调用 `scripts/graphrag_runner.py`，执行 ms-graphrag 流水线
- **输出**：Parquet 文件路径 & 图谱统计信息
- **存储**：`data/outputs/graphrag/`

## API 设计
