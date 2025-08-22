# AI 功能后端 - 智能教育助手

基于 FastAPI 构建的 AI 功能后端，提供完整的智能教育解决方案，包括文档大纲生成、RAG 问答、智能聊天等功能。

## 🚀 项目概述

这是一个现代化的 AI 后端服务，专为教育场景设计，提供文档处理、知识问答、智能对话等核心功能。

### 核心特性

- **📝 文档大纲生成**: 智能分析文档内容，生成结构化三层次大纲
- **🔍 RAG 问答系统**: 基于向量数据库的检索增强生成，支持精确的知识问答
- **💬 智能对话**: 多模式聊天引擎，支持文档问答和自由对话
- **🎯 统一处理**: 一站式文件处理流程，自动完成大纲生成和索引建立
- **🛡️ 企业级安全**: 完整的文件验证、错误处理和性能监控

### 技术架构

- **Web 框架**: FastAPI 0.116.1 - 高性能异步 Web 框架
- **AI 引擎**: OpenAI GPT-4o-mini - 强大的语言模型
- **向量数据库**: Qdrant 1.15.1 - 高性能向量搜索引擎
- **缓存存储**: Redis 5.0+ - 对话记忆和会话管理
- **文档处理**: LlamaIndex 0.13.0 - 专业的文档索引和检索框架

## 🛠️ 环境要求

### 系统要求

- Python 3.8+
- Redis 服务器
- Qdrant 向量数据库

### 外部服务

- OpenAI API 或兼容的 API 服务

## ⚡ 快速开始

### 1. 环境准备

```bash
# 确保 Python 3.11 已安装
python --version

# 创建虚拟环境（如果还没有）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置你的 OpenAI API 密钥
# API_KEY=your_openai_api_key_here
```

### 3. 启动服务

```bash
# 开发模式启动
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

启动后访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API 接口文档

### 🌐 基础信息

- **服务地址**: `http://localhost:8000`
- **API 版本**: `/api/v1`
- **文档地址**:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`
- **健康检查**: `http://localhost:8000/health`

### 📋 API 概览

| 模块     | 功能         | 端点                                                          | 方法   |
| -------- | ------------ | ------------------------------------------------------------- | ------ |
| 大纲生成 | 生成文档大纲 | `/api/v1/outline/generate`                                    | POST   |
| 大纲生成 | 查询任务状态 | `/api/v1/outline/task/{task_id}`                              | GET    |
| 大纲生成 | 获取大纲文件 | `/api/v1/outline/file/{course_id}/{course_material_id}`       | GET    |
| 大纲生成 | 获取性能指标 | `/api/v1/outline/metrics`                                     | GET    |
| RAG 索引 | 建立文档索引 | `/api/v1/rag/index`                                           | POST   |
| RAG 索引 | 获取集合列表 | `/api/v1/rag/collections`                                     | GET    |
| RAG 索引 | 删除集合     | `/api/v1/rag/collections/{collection_name}`                   | DELETE |
| 智能聊天 | 智能对话     | `/api/v1/conversation/chat`                                   | POST   |
| 智能聊天 | 清除会话     | `/api/v1/conversation/conversations/{conversation_id}`        | DELETE |
| 智能聊天 | 获取会话状态 | `/api/v1/conversation/conversations/{conversation_id}/status` | GET    |
| 智能聊天 | 获取引擎列表 | `/api/v1/conversation/engines`                                | GET    |
| 课程材料 | 统一处理材料 | `/api/v1/course-materials/process`                            | POST   |
| 课程材料 | 查询处理状态 | `/api/v1/course-materials/tasks/{task_id}/status`             | GET    |
| 课程材料 | 清理指定材料 | `/api/v1/course-materials/{course_id}/{course_material_id}`   | DELETE |
| 课程管理 | 删除整个课程 | `/api/v1/course/{course_id}`                                  | DELETE |

---

## 🎯 核心功能使用指南

### 1. 📝 文档大纲生成

智能分析文档内容，生成结构化的三层次大纲。

#### 基本用法

```bash
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -F "file=@document.md" \
  -F "course_id=CS101" \
  -F "course_material_id=lesson01" \
  -F "material_name=Python基础教程"
```

#### 响应示例

```json
{
  "task_id": "uuid-task-id",
  "status": "completed",
  "message": "大纲生成成功",
  "outline_content": "# Python编程基础\n\n## 变量与数据类型\n### 数字类型...",
  "processing_time": 15.5,
  "token_usage": {
    "total_tokens": 2300
  }
}
```

### 2. 🔍 RAG 问答系统

基于向量数据库的检索增强生成，支持精确的知识问答。

#### 建立文档索引

```bash
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -F "file=@document.md" \
  -F "course_id=CS101" \
  -F "course_material_id=lesson01" \
  -F "collection_name=course_materials"
```

#### 智能问答

```bash
curl -X POST "http://localhost:8000/api/v1/conversation/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user_session_123",
    "question": "什么是Python变量？",
    "course_id": "CS101",
    "chat_engine_type": "condense_plus_context"
  }'
```

### 3. 🎯 统一处理流程

一站式文件处理，自动完成大纲生成和索引建立。

```bash
curl -X POST "http://localhost:8000/api/v1/course-materials/process" \
  -F "file=@document.md" \
  -F "course_id=CS101" \
  -F "course_material_id=lesson01" \
  -F "material_name=Python基础教程" \
  -F "enable_rag_indexing=true"
```

---

## 📚 详细 API 文档

### 大纲生成模块

| 端点                                             | 方法 | 功能         |
| ------------------------------------------------ | ---- | ------------ |
| `/api/v1/outline/generate`                       | POST | 生成文档大纲 |
| `/api/v1/outline/task/{task_id}`                 | GET  | 查询任务状态 |
| `/api/v1/outline/file/{course_id}/{material_id}` | GET  | 获取大纲文件 |
| `/api/v1/outline/metrics`                        | GET  | 获取性能指标 |

### RAG 系统模块

| 端点                             | 方法   | 功能         |
| -------------------------------- | ------ | ------------ |
| `/api/v1/rag/index`              | POST   | 建立文档索引 |
| `/api/v1/rag/collections`        | GET    | 获取集合列表 |
| `/api/v1/rag/collections/{name}` | DELETE | 删除集合     |
| `/api/v1/rag/health`             | GET    | 健康检查     |

### 智能对话模块

| 端点                                      | 方法   | 功能         |
| ----------------------------------------- | ------ | ------------ |
| `/api/v1/conversation/chat`               | POST   | 智能对话     |
| `/api/v1/conversation/engines`            | GET    | 获取引擎列表 |
| `/api/v1/conversation/conversations/{id}` | DELETE | 清除会话     |
| `/api/v1/conversation/health`             | GET    | 健康检查     |

---

## 🏗️ 项目结构

```
rwai_fastapi/
├── app/                          # 应用主目录
│   ├── api/                     # API 路由
│   │   └── v1/                  # API v1 版本
│   │       ├── outline.py       # 大纲生成 API
│   │       ├── rag.py           # RAG 索引 API
│   │       ├── conversation.py  # 智能对话 API
│   │       ├── course_materials.py # 统一材料处理 API
│   │       └── course.py        # 课程管理 API
│   ├── core/                    # 核心模块
│   │   ├── config.py           # 配置管理
│   │   ├── logging.py          # 日志配置
│   │   └── deps.py             # 依赖注入
│   ├── schemas/                 # 数据模型
│   ├── services/                # 业务逻辑
│   │   ├── outline/            # 大纲生成服务
│   │   ├── rag/                # RAG 服务
│   │   └── course_material/    # 课程材料服务
│   ├── utils/                   # 工具函数
│   └── main.py                 # 应用入口
├── data/                        # 数据目录
│   ├── uploads/                # 上传文件
│   └── outputs/                # 输出文件
├── frontend/                    # 前端文件
├── requirements.txt             # 依赖列表
└── README.md                   # 项目文档
```

---

## � 配置说明

### 环境变量

| 变量名            | 描述            | 默认值                      |
| ----------------- | --------------- | --------------------------- |
| `OPENAI_API_KEY`  | OpenAI API 密钥 | 必需                        |
| `OPENAI_BASE_URL` | API 基础 URL    | `https://api.openai.com/v1` |
| `OUTLINE_MODEL`   | 大纲生成模型    | `gpt-4o-mini`               |
| `REFINE_MODEL`    | 精简模型        | `gpt-4o-mini`               |
| `REDIS_URL`       | Redis 连接 URL  | `redis://localhost:6379`    |
| `QDRANT_HOST`     | Qdrant 主机     | `localhost`                 |
| `QDRANT_PORT`     | Qdrant 端口     | `6333`                      |

### 模型配置

- **LLM 模型**: `gpt-4o-mini` - 用于大纲生成和对话
- **嵌入模型**: `text-embedding-3-small` - 用于向量化
- **温度参数**: `0.1` - 保证输出稳定性
- **Token 限制**: `4000` - 对话记忆限制

---

## 🚀 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -t rwai-fastapi .

# 运行容器
docker run -p 8000:8000 --env-file .env rwai-fastapi
```

### Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - QDRANT_HOST=qdrant
    depends_on:
      - redis
      - qdrant

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
```

---

## 🧪 测试指南

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-mock

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_outline.py

# 生成覆盖率报告
pytest --cov=app tests/
```

### API 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 测试大纲生成
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -F "file=@test.md" \
  -F "course_id=TEST" \
  -F "course_material_id=001" \
  -F "material_name=测试文档"

# 测试RAG问答
curl -X POST "http://localhost:8000/api/v1/conversation/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_session",
    "question": "这个文档讲了什么？",
    "chat_engine_type": "condense_plus_context"
  }'
```

---

## 🔍 故障排除

### 常见问题

1. **OpenAI API 连接失败**

   - 检查 API 密钥是否正确
   - 确认网络连接正常
   - 验证 API 配额是否充足

2. **Redis 连接失败**

   - 确认 Redis 服务正在运行
   - 检查连接 URL 配置
   - 验证端口是否被占用

3. **Qdrant 连接失败**
   - 确认 Qdrant 服务正在运行
   - 检查主机和端口配置
   - 验证防火墙设置

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

---

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

- 项目链接: [https://github.com/your-username/rwai_fastapi](https://github.com/your-username/rwai_fastapi)
- 问题反馈: [Issues](https://github.com/your-username/rwai_fastapi/issues)

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [LlamaIndex](https://www.llamaindex.ai/) - 专业的文档索引和检索框架
- [Qdrant](https://qdrant.tech/) - 高性能向量搜索引擎
- [OpenAI](https://openai.com/) - 强大的语言模型服务
