# RAG 问答系统 API 文档

基于 LlamaIndex 和 Qdrant 的检索增强生成（RAG）问答系统，提供智能文档问答和对话功能。

## 🎯 系统概述

RAG 系统通过以下步骤实现智能问答：

1. **文档索引**: 将文档分块并转换为向量存储在 Qdrant 中
2. **智能检索**: 根据用户问题检索相关文档片段
3. **增强生成**: 结合检索内容和 LLM 生成准确回答
4. **对话记忆**: 使用 Redis 维护多轮对话上下文

## 🔧 技术架构

- **向量数据库**: Qdrant 1.15.1
- **文档处理**: LlamaIndex 0.13.0
- **嵌入模型**: text-embedding-3-small
- **语言模型**: gpt-4o-mini
- **对话存储**: Redis 5.0+

## 📋 API 端点概览

### 文档索引管理

| 端点 | 方法 | 功能 | 描述 |
|------|------|------|------|
| `/api/v1/rag/index` | POST | 建立文档索引 | 上传文档并建立向量索引 |
| `/api/v1/rag/collections` | GET | 获取集合列表 | 查看所有向量集合 |
| `/api/v1/rag/collections/{name}` | GET | 获取集合信息 | 查看特定集合详情 |
| `/api/v1/rag/collections/{name}` | DELETE | 删除集合 | 删除整个向量集合 |
| `/api/v1/rag/collections/{name}/count` | GET | 统计文档数量 | 获取集合中的文档数量 |

### 文档管理

| 端点 | 方法 | 功能 | 描述 |
|------|------|------|------|
| `/api/v1/rag/documents/course/{course_id}` | DELETE | 删除课程文档 | 删除指定课程的所有文档 |
| `/api/v1/rag/documents/material/{course_id}/{material_id}` | DELETE | 删除材料文档 | 删除指定材料的文档 |

### 智能对话

| 端点 | 方法 | 功能 | 描述 |
|------|------|------|------|
| `/api/v1/conversation/chat` | POST | 智能问答 | 基于文档的智能对话 |
| `/api/v1/conversation/engines` | GET | 获取引擎列表 | 查看可用的聊天引擎 |
| `/api/v1/conversation/conversations/{id}` | DELETE | 清除会话 | 删除对话历史 |
| `/api/v1/conversation/conversations/{id}/status` | GET | 获取会话状态 | 查看会话信息 |
| `/api/v1/conversation/config` | GET | 获取配置信息 | 查看系统配置 |

### 系统监控

| 端点 | 方法 | 功能 | 描述 |
|------|------|------|------|
| `/api/v1/rag/health` | GET | RAG 健康检查 | 检查 RAG 系统状态 |
| `/api/v1/conversation/health` | GET | 对话健康检查 | 检查对话系统状态 |

## 🚀 核心功能详解

### 1. 文档索引建立

#### 基本用法

```bash
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -F "file=@document.md" \
  -F "course_id=CS101" \
  -F "course_material_id=lesson01" \
  -F "collection_name=course_materials"
```

#### 请求参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `file` | File | 是 | 文档文件（.md/.txt） |
| `course_id` | String | 是 | 课程标识符 |
| `course_material_id` | String | 是 | 材料标识符 |
| `collection_name` | String | 否 | 集合名称（默认：course_materials） |

#### 响应示例

```json
{
  "success": true,
  "message": "文档索引建立成功",
  "document_count": 1,
  "chunk_count": 15,
  "processing_time": 8.5,
  "collection_name": "course_materials",
  "metadata": {
    "course_id": "CS101",
    "course_material_id": "lesson01",
    "file_name": "document.md",
    "file_size": 2048,
    "chunk_size": 512,
    "chunk_overlap": 50
  }
}
```

### 2. 智能问答对话

#### 基本用法

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

#### 请求参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `conversation_id` | String | 是 | 会话标识符 |
| `question` | String | 是 | 用户问题 |
| `chat_engine_type` | String | 是 | 引擎类型（见下表） |
| `course_id` | String | 否 | 课程过滤条件 |
| `course_material_id` | String | 否 | 材料过滤条件 |
| `collection_name` | String | 否 | 集合名称 |

#### 聊天引擎类型

| 类型 | 名称 | 描述 | 适用场景 |
|------|------|------|----------|
| `condense_plus_context` | 检索增强模式 | 基于文档内容的智能问答 | 知识查询、专业问答 |
| `simple` | 直接对话模式 | 不检索文档的自由对话 | 一般聊天、创意讨论 |

#### 响应示例

```json
{
  "answer": "Python中的变量是用来存储数据的容器。变量可以存储不同类型的数据，如数字、字符串、列表等。在Python中，变量不需要声明类型，可以直接赋值使用。",
  "sources": [
    {
      "content": "变量是Python编程的基础概念，用于存储和操作数据...",
      "metadata": {
        "course_id": "CS101",
        "course_material_id": "lesson01",
        "file_path": "data/uploads/CS101/lesson01_python_basics.md",
        "chunk_id": "chunk_001"
      },
      "score": 0.92
    }
  ],
  "conversation_id": "user_session_123",
  "chat_engine_type": "condense_plus_context",
  "filter_info": "过滤条件: course_id=CS101",
  "processing_time": 2.3,
  "token_usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 150,
    "total_tokens": 1350
  }
}
```

### 3. 集合管理

#### 获取所有集合

```bash
curl http://localhost:8000/api/v1/rag/collections
```

#### 响应示例

```json
{
  "collections": [
    {
      "name": "course_materials",
      "vectors_count": 1250,
      "indexed_vectors_count": 1250,
      "points_count": 1250,
      "segments_count": 1,
      "config": {
        "params": {
          "vectors": {
            "size": 1536,
            "distance": "Cosine"
          }
        }
      },
      "status": "green"
    }
  ],
  "total_collections": 1
}
```

#### 删除集合

```bash
curl -X DELETE http://localhost:8000/api/v1/rag/collections/course_materials
```

### 4. 文档过滤和检索

#### 按课程过滤

```json
{
  "conversation_id": "session_123",
  "question": "这门课程的主要内容是什么？",
  "course_id": "CS101",
  "chat_engine_type": "condense_plus_context"
}
```

#### 按材料过滤

```json
{
  "conversation_id": "session_123",
  "question": "这个章节讲了什么？",
  "course_material_id": "lesson01",
  "chat_engine_type": "condense_plus_context"
}
```

## 🔧 配置参数

### RAG 系统配置

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `REDIS_URL` | `redis://localhost:6379` | Redis 连接地址 |
| `REDIS_TTL` | `3600` | Redis 数据过期时间（秒） |
| `QDRANT_HOST` | `localhost` | Qdrant 主机地址 |
| `QDRANT_PORT` | `6333` | Qdrant 端口 |
| `LLM_MODEL` | `gpt-4o-mini` | 语言模型名称 |
| `EMBED_MODEL` | `text-embedding-3-small` | 嵌入模型名称 |
| `CHUNK_SIZE` | `512` | 文本分块大小 |
| `CHUNK_OVERLAP` | `50` | 文本分块重叠 |

### 对话系统配置

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `CONVERSATION_TOKEN_LIMIT` | `4000` | 对话记忆 Token 限制 |
| `CONVERSATION_SIMILARITY_TOP_K` | `6` | 检索相似文档数量 |
| `LLM_TEMPERATURE` | `0.1` | 模型温度参数 |

## 🧪 测试示例

### JavaScript 客户端

```javascript
class RAGClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  // 建立文档索引
  async indexDocument(file, courseId, materialId, collectionName = 'course_materials') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('course_id', courseId);
    formData.append('course_material_id', materialId);
    formData.append('collection_name', collectionName);

    const response = await fetch(`${this.baseUrl}/api/v1/rag/index`, {
      method: 'POST',
      body: formData
    });

    return await response.json();
  }

  // 智能问答
  async chat(conversationId, question, options = {}) {
    const requestBody = {
      conversation_id: conversationId,
      question: question,
      chat_engine_type: options.engineType || 'condense_plus_context',
      ...options
    };

    const response = await fetch(`${this.baseUrl}/api/v1/conversation/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    return await response.json();
  }

  // 获取集合列表
  async getCollections() {
    const response = await fetch(`${this.baseUrl}/api/v1/rag/collections`);
    return await response.json();
  }
}

// 使用示例
const client = new RAGClient();

// 1. 建立索引
const indexResult = await client.indexDocument(
  fileInput.files[0],
  'CS101',
  'lesson01'
);
console.log('索引建立结果:', indexResult);

// 2. 开始对话
const chatResult = await client.chat(
  'user_session_123',
  '什么是Python变量？',
  { course_id: 'CS101' }
);
console.log('AI回答:', chatResult.answer);
```

## 🔍 故障排除

### 常见问题

1. **Qdrant 连接失败**
   ```
   Error: 无法连接到向量数据库
   ```
   - 检查 Qdrant 服务是否运行
   - 验证 `QDRANT_HOST` 和 `QDRANT_PORT` 配置

2. **Redis 连接失败**
   ```
   Error: Redis connection failed
   ```
   - 检查 Redis 服务状态
   - 验证 `REDIS_URL` 配置

3. **文档索引失败**
   ```
   Error: 文档处理失败
   ```
   - 确认文件格式为 .md 或 .txt
   - 检查文件大小是否超过限制

### 调试命令

```bash
# 检查 Qdrant 状态
curl http://localhost:6333/health

# 检查 Redis 连接
redis-cli ping

# 查看集合信息
curl http://localhost:8000/api/v1/rag/collections

# 测试健康检查
curl http://localhost:8000/api/v1/rag/health
```

---

## 📊 性能指标

| 操作 | 平均响应时间 | 吞吐量 | 备注 |
|------|-------------|--------|------|
| 文档索引 | 5-15秒 | 20 docs/min | 取决于文档大小 |
| 智能问答 | 2-8秒 | 100 queries/min | 取决于检索范围 |
| 集合查询 | <1秒 | 1000 requests/min | 缓存优化 |

## 🔒 安全考虑

- 文件上传限制：仅支持 .md 和 .txt 格式
- 大小限制：单文件最大 10MB
- 访问控制：基于课程和材料 ID 的数据隔离
- 会话管理：Redis TTL 自动清理过期会话

---

**🎯 RAG 系统为您的应用提供强大的文档问答能力！**
