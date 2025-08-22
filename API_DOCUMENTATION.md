# AI 功能后端 API 文档

## 📋 API 概览

**基础信息**

- **服务地址**: `http://localhost:8000`
- **API 版本**: `/api/v1`
- **文档地址**:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`
- **健康检查**: `http://localhost:8000/health`

**支持的内容类型**

- `application/json` - JSON 数据
- `multipart/form-data` - 文件上传

---

## 🌐 基础端点

### 健康检查

**端点**: `GET /health`

**描述**: 检查服务健康状态

**响应示例**:

```json
{
  "status": "healthy",
  "version": "1.2.0",
  "uptime": 3600.5,
  "openai_api": "configured"
}
```

### 根路径

**端点**: `GET /`

**描述**: 获取 API 基本信息

**响应示例**:

```json
{
  "name": "AI Backend API",
  "version": "1.2.0",
  "description": "智能教育助手后端API",
  "docs_url": "/docs",
  "redoc_url": "/redoc",
  "health_check": "/health"
}
```

---

## 📝 大纲生成模块

### 1. 生成文档大纲

**端点**: `POST /api/v1/outline/generate`

**描述**: 上传文档文件并生成结构化大纲

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `file` | File | ✅ | 文档文件（.md/.txt，最大 10MB） |
| `course_id` | String | ✅ | 课程 ID |
| `course_material_id` | String | ✅ | 课程材料 ID（课程内唯一） |
| `material_name` | String | ✅ | 材料名称 |

**cURL 示例**:

```bash
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -F "file=@python基础.md" \
  -F "course_id=CS101" \
  -F "course_material_id=001" \
  -F "material_name=Python基础"
```

**响应示例**:

```json
{
  "task_id": "12345678-1234-1234-1234-123456789012",
  "status": "completed",
  "message": "大纲生成成功",
  "course_id": "CS101",
  "course_material_id": "001",
  "material_name": "Python基础",
  "outline_content": "# Python编程基础\n\n## 变量与数据类型\n### 数字类型...",
  "outline_file_path": "data/outputs/outlines/CS101/001_Python基础.md",
  "original_file_path": "data/uploads/CS101/001_Python基础.md",
  "processing_time": 15.5,
  "token_usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 800,
    "total_tokens": 2300
  },
  "created_at": "2024-08-22T10:30:00",
  "completed_at": "2024-08-22T10:30:15"
}
```

### 2. 查询任务状态

**端点**: `GET /api/v1/outline/task/{task_id}`

**描述**: 查询大纲生成任务的状态

**路径参数**:
| 参数名 | 类型 | 描述 |
|--------|------|------|
| `task_id` | String | 任务 ID |

**响应示例**:

```json
{
  "task_id": "12345678-1234-1234-1234-123456789012",
  "status": "processing",
  "message": "大纲生成中",
  "course_id": "CS101",
  "course_material_id": "001",
  "material_name": "Python基础",
  "original_filename": "python基础.md",
  "file_size": 15360,
  "created_at": "2024-08-22T10:30:00"
}
```

**任务状态说明**:

- `pending`: 等待处理
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败

### 3. 获取大纲文件

**端点**: `GET /api/v1/outline/file/{course_id}/{course_material_id}`

**描述**: 获取指定课程材料的大纲文件内容

**路径参数**:
| 参数名 | 类型 | 描述 |
|--------|------|------|
| `course_id` | String | 课程 ID |
| `course_material_id` | String | 课程材料 ID |

**响应示例**:

```json
{
  "success": true,
  "message": "文件获取成功",
  "course_id": "CS101",
  "course_material_id": "001",
  "material_name": "Python基础",
  "file_path": "data/outputs/outlines/CS101/001_Python基础.md",
  "file_content": "# Python编程基础\n\n## 变量与数据类型\n### 数字类型...",
  "file_size": 2048,
  "last_modified": "2024-08-22T10:30:00"
}
```

### 4. 获取性能指标

**端点**: `GET /api/v1/outline/metrics`

**描述**: 获取大纲生成模块的性能指标

**响应示例**:

```json
{
  "performance_metrics": {
    "total_requests": 150,
    "average_processing_time": 18.5,
    "success_rate": 0.96
  },
  "active_tasks": 3,
  "total_tasks": 150
}
```

---

## 🔍 RAG 文档索引模块

### 1. 建立文档索引

**端点**: `POST /api/v1/rag/index`

**描述**: 为上传的文档建立向量索引，用于后续的智能问答

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `file` | File | ✅ | 文档文件（.md/.txt） |
| `course_id` | String | ✅ | 课程 ID |
| `course_material_id` | String | ✅ | 课程材料 ID |
| `collection_name` | String | ❌ | 集合名称（默认使用配置） |

**响应示例**:

```json
{
  "success": true,
  "message": "文档索引建立成功",
  "document_count": 1,
  "chunk_count": 15,
  "processing_time": 8.5,
  "collection_name": "course_materials"
}
```

### 2. 获取集合列表

**端点**: `GET /api/v1/rag/collections`

**描述**: 获取所有向量集合的列表

**响应示例**:

```json
{
  "collections": [
    {
      "name": "course_materials",
      "vectors_count": 1250,
      "indexed_only": false,
      "payload_schema": {
        "course_id": "keyword",
        "course_material_id": "keyword"
      }
    }
  ],
  "total_count": 1
}
```

### 3. 删除集合

**端点**: `DELETE /api/v1/rag/collections/{collection_name}`

**描述**: 删除指定的向量集合

**路径参数**:
| 参数名 | 类型 | 描述 |
|--------|------|------|
| `collection_name` | String | 集合名称 |

**响应示例**:

```json
{
  "success": true,
  "message": "集合删除成功",
  "collection_name": "course_materials"
}
```

---

## 💬 智能聊天模块

### 1. 智能对话

**端点**: `POST /api/v1/conversation/chat`

**描述**: 与 AI 进行智能对话，支持基于文档的问答和自由聊天

**请求格式**: `application/json`

**请求参数**:
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `conversation_id` | String | ✅ | 会话 ID |
| `question` | String | ✅ | 用户问题 |
| `chat_engine_type` | String | ✅ | 引擎类型 |
| `course_id` | String | ❌ | 课程 ID（与 course_material_id 二选一） |
| `course_material_id` | String | ❌ | 材料 ID（与 course_id 二选一） |
| `collection_name` | String | ❌ | 集合名称 |

**聊天引擎类型**:

- `condense_plus_context`: 检索增强模式，基于文档内容回答
- `simple`: 直接对话模式，不检索文档

**请求示例**:

```json
{
  "conversation_id": "user123_session1",
  "question": "Python中的变量是什么？",
  "chat_engine_type": "condense_plus_context",
  "course_id": "CS101"
}
```

**响应示例**:

```json
{
  "answer": "Python中的变量是用来存储数据的容器。变量可以存储不同类型的数据，如数字、字符串、列表等...",
  "sources": [
    {
      "content": "变量是Python编程的基础概念...",
      "metadata": {
        "course_id": "CS101",
        "course_material_id": "001",
        "file_path": "data/uploads/CS101/001_Python基础.md"
      },
      "score": 0.85
    }
  ],
  "conversation_id": "user123_session1",
  "chat_engine_type": "condense_plus_context",
  "filter_info": "过滤条件: course_id=CS101",
  "processing_time": 2.3
}
```

### 2. 清除会话记录

**端点**: `DELETE /api/v1/conversation/conversations/{conversation_id}`

**描述**: 清除指定会话的聊天记录

**路径参数**:
| 参数名 | 类型 | 描述 |
|--------|------|------|
| `conversation_id` | String | 会话 ID |

**响应示例**:

```json
{
  "success": true,
  "message": "会话记录已清除",
  "conversation_id": "user123_session1",
  "cleared_messages": 15
}
```

### 3. 获取会话状态

**端点**: `GET /api/v1/conversation/conversations/{conversation_id}/status`

**描述**: 获取指定会话的状态信息

**路径参数**:
| 参数名 | 类型 | 描述 |
|--------|------|------|
| `conversation_id` | String | 会话 ID |

**响应示例**:

```json
{
  "conversation_id": "user123_session1",
  "exists": true,
  "message_count": 10,
  "last_activity": "2024-08-22T10:30:00",
  "memory_usage": {
    "token_count": 2500,
    "summary": "用户询问了Python基础概念..."
  }
}
```

### 4. 获取可用引擎

**端点**: `GET /api/v1/conversation/engines`

**描述**: 获取所有可用的聊天引擎类型和配置信息

**响应示例**:

```json
{
  "engines": [
    {
      "type": "condense_plus_context",
      "name": "检索增强模式",
      "description": "基于文档内容的智能问答，适合知识查询",
      "features": [
        "向量检索",
        "上下文整合",
        "来源追踪",
        "动态过滤",
        "问题压缩",
        "对话记忆"
      ],
      "use_cases": ["课程内容问答", "文档知识查询", "专业领域咨询"]
    },
    {
      "type": "simple",
      "name": "直接对话模式",
      "description": "与AI直接对话，不检索文档，适合一般聊天",
      "features": ["快速响应", "对话记忆", "自然交流", "多轮对话"],
      "use_cases": ["一般性聊天", "创意讨论", "问题澄清"]
    }
  ],
  "configuration": {
    "memory_management": "Redis-based chat store",
    "prompt_templates": "File-based templates",
    "vector_search": "Qdrant vector database",
    "llm_backend": "OpenAI compatible API"
  }
}
```

### 5. 获取对话配置

**端点**: `GET /api/v1/conversation/config`

**描述**: 获取对话服务的配置信息

**响应示例**:

```json
{
  "configuration": {
    "qdrant_url": "http://localhost:6333",
    "redis_url": "redis://localhost:6379",
    "embedding_model": "text-embedding-3-small",
    "llm_model": "gpt-4o-mini"
  },
  "components": {
    "qdrant": "connected",
    "redis": "connected",
    "openai": "configured"
  },
  "supported_engines": ["condense_plus_context", "simple"]
}
```

### 6. 聊天服务健康检查

**端点**: `GET /api/v1/conversation/health`

**描述**: 检查聊天服务的健康状态

**响应示例**:

```json
{
  "status": "healthy",
  "components": {
    "rag_config": "initialized",
    "memory_store": "connected",
    "chat_engines": "available"
  },
  "active_conversations": 25,
  "total_messages": 1250
}
```

---

## 🎯 统一课程材料处理模块

### 1. 一站式材料处理

**端点**: `POST /api/v1/course-materials/process`

**描述**: 统一处理课程材料，自动完成文件上传、大纲生成、RAG 索引建立的全流程

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `file` | File | ✅ | 课程材料文件（.md/.txt） |
| `course_id` | String | ✅ | 课程 ID |
| `course_material_id` | String | ✅ | 课程材料 ID |
| `material_name` | String | ✅ | 材料名称 |
| `custom_prompt` | String | ❌ | 自定义提示词 |
| `include_refine` | Boolean | ❌ | 是否精简大纲（默认 true） |
| `model_name` | String | ❌ | 指定模型名称 |
| `enable_rag_indexing` | Boolean | ❌ | 是否建立 RAG 索引（默认 true） |
| `rag_collection_name` | String | ❌ | RAG 集合名称 |

**响应示例**:

```json
{
  "task_id": "12345678-1234-1234-1234-123456789012",
  "status": "completed",
  "message": "课程材料处理完成",
  "current_step": "completed",
  "completed_steps": 3,
  "total_steps": 3,
  "progress_percentage": 100.0,
  "course_id": "CS101",
  "course_material_id": "001",
  "material_name": "Python基础",
  "upload_file_path": "data/uploads/CS101/001_Python基础.md",
  "outline_file_path": "data/outputs/outlines/CS101/001_Python基础.md",
  "outline_content": "# Python编程基础\n\n## 变量与数据类型\n### 数字类型...",
  "rag_index_status": "completed",
  "rag_collection_name": "course_materials",
  "rag_document_count": 15,
  "total_processing_time": 45.5,
  "processing_steps": [
    {
      "step_name": "file_upload",
      "status": "completed",
      "message": "文件上传成功",
      "processing_time": 2.1
    },
    {
      "step_name": "outline_generation",
      "status": "completed",
      "message": "大纲生成成功",
      "processing_time": 25.8
    },
    {
      "step_name": "rag_indexing",
      "status": "completed",
      "message": "RAG索引建立成功",
      "processing_time": 17.6
    }
  ],
  "created_at": "2024-08-22T10:30:00",
  "completed_at": "2024-08-22T10:30:45"
}
```

**处理状态说明**:

- `uploading`: 文件上传中
- `outline_generating`: 大纲生成中
- `rag_indexing`: RAG 索引建立中
- `completed`: 处理完成
- `failed`: 处理失败

### 2. 查询处理状态

**端点**: `GET /api/v1/course-materials/tasks/{task_id}/status`

**描述**: 查询课程材料处理任务的实时状态和进度

**路径参数**:
| 参数名 | 类型 | 描述 |
|--------|------|------|
| `task_id` | String | 任务 ID |

**响应示例**:

```json
{
  "task_id": "12345678-1234-1234-1234-123456789012",
  "status": "outline_generating",
  "message": "正在生成大纲",
  "current_step": "outline_generation",
  "completed_steps": 1,
  "total_steps": 3,
  "progress_percentage": 33.3,
  "course_id": "CS101",
  "course_material_id": "001",
  "material_name": "Python基础",
  "original_filename": "python基础.md",
  "file_size": 15360,
  "upload_file_path": "data/uploads/CS101/001_Python基础.md",
  "created_at": "2024-08-22T10:30:00",
  "last_updated": "2024-08-22T10:30:15"
}
```

### 3. 清理指定材料

**端点**: `DELETE /api/v1/course-materials/{course_id}/{course_material_id}`

**描述**: 删除指定课程材料的所有数据，包括文件、大纲、RAG 索引等

**路径参数**:
| 参数名 | 类型 | 描述 |
|--------|------|------|
| `course_id` | String | 课程 ID |
| `course_material_id` | String | 课程材料 ID |

**查询参数**:
| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `cleanup_files` | Boolean | true | 是否删除文件 |
| `cleanup_rag_data` | Boolean | true | 是否删除 RAG 数据 |
| `cleanup_task_data` | Boolean | true | 是否删除任务数据 |

**响应示例**:

```json
{
  "success": true,
  "message": "课程材料清理完成",
  "course_id": "CS101",
  "course_material_id": "001",
  "cleanup_operations": [
    {
      "type": "files",
      "success": true,
      "message": "文件删除成功"
    },
    {
      "type": "rag_data",
      "success": true,
      "message": "RAG数据删除成功",
      "deleted_vectors": 15
    },
    {
      "type": "task_data",
      "success": true,
      "message": "任务数据删除成功"
    }
  ],
  "processing_time": 1.5
}
```

### 4. 健康检查

**端点**: `GET /api/v1/course-materials/health`

**描述**: 检查课程材料处理服务的健康状态

**响应示例**:

```json
{
  "status": "healthy",
  "message": "课程材料处理服务运行正常",
  "components": {
    "outline_service": "available",
    "rag_service": "available",
    "cleanup_service": "available",
    "file_system": "available"
  }
}
```

---

## 🗂️ 课程管理模块

### 1. 删除整个课程

**端点**: `DELETE /api/v1/course/{course_id}`

**描述**: 删除整个课程及其所有材料和数据

**路径参数**:
| 参数名 | 类型 | 描述 |
|--------|------|------|
| `course_id` | String | 课程 ID |

**响应示例**:

```json
{
  "success": true,
  "message": "课程删除成功",
  "course_id": "CS101",
  "operations": [
    {
      "type": "upload_folder",
      "success": true,
      "path": "data/uploads/CS101"
    },
    {
      "type": "outline_folder",
      "success": true,
      "path": "data/outputs/outlines/CS101"
    },
    {
      "type": "rag_vectors",
      "success": true,
      "deleted_count": 45
    }
  ],
  "processing_time": 1.2
}
```

---

## ⚠️ 错误处理

### 错误响应格式

所有 API 错误都遵循统一的响应格式：

```json
{
  "error": "error_type",
  "message": "错误描述",
  "detail": "详细错误信息",
  "task_id": "相关任务ID（如果有）",
  "timestamp": "2024-08-22T10:30:00"
}
```

### 常见错误码

| HTTP 状态码 | 错误类型                 | 描述                | 解决方案                         |
| ----------- | ------------------------ | ------------------- | -------------------------------- |
| 400         | `validation_error`       | 请求参数验证失败    | 检查请求参数格式和必需字段       |
| 400         | `file_validation_error`  | 文件验证失败        | 确认文件格式(.md/.txt)和大小限制 |
| 400         | `duplicate_material_id`  | 课程材料 ID 重复    | 使用不同的 course_material_id    |
| 404         | `task_not_found`         | 任务不存在          | 检查 task_id 是否正确            |
| 404         | `file_not_found`         | 文件不存在          | 确认课程 ID 和材料 ID 是否正确   |
| 404         | `conversation_not_found` | 会话不存在          | 检查 conversation_id 是否正确    |
| 500         | `internal_error`         | 服务器内部错误      | 查看服务器日志，联系管理员       |
| 500         | `openai_api_error`       | OpenAI API 调用失败 | 检查 API 密钥和网络连接          |
| 500         | `qdrant_error`           | 向量数据库错误      | 检查 Qdrant 服务状态             |
| 500         | `redis_error`            | Redis 连接错误      | 检查 Redis 服务状态              |

### 错误示例

**文件验证失败**:

```json
{
  "error": "file_validation_error",
  "message": "文件验证失败",
  "detail": "不支持的文件类型: .pdf。支持的类型: .md, .txt",
  "timestamp": "2024-08-22T10:30:00"
}
```

**课程材料 ID 重复**:

```json
{
  "error": "duplicate_material_id",
  "message": "课程材料ID重复",
  "detail": "课程材料ID '001' 在课程 'CS101' 中已存在",
  "timestamp": "2024-08-22T10:30:00"
}
```

**任务不存在**:

```json
{
  "error": "task_not_found",
  "message": "任务不存在",
  "detail": "未找到ID为 '12345678-1234-1234-1234-123456789012' 的任务",
  "timestamp": "2024-08-22T10:30:00"
}
```

---

## 🔐 认证和安全

### 认证方式

当前版本暂不需要 API 认证，但建议在生产环境中实施以下安全措施：

1. **API 密钥认证**
2. **JWT 令牌认证**
3. **IP 白名单**
4. **请求频率限制**

### 安全最佳实践

- 使用 HTTPS 协议
- 验证所有输入参数
- 限制文件上传大小
- 实施请求频率限制
- 记录所有 API 访问日志

---

## 📊 API 限制

### 请求限制

| 项目     | 限制      | 说明                 |
| -------- | --------- | -------------------- |
| 文件大小 | 10MB      | 单个文件最大大小     |
| 文件格式 | .md, .txt | 支持的文件类型       |
| 并发请求 | 50 个     | 同时处理的请求数     |
| 任务超时 | 5 分钟    | 单个任务最大处理时间 |
| 会话数量 | 1000 个   | 同时活跃的会话数     |

### 频率限制

| 端点类型 | 限制   | 时间窗口 |
| -------- | ------ | -------- |
| 文件上传 | 10 次  | 每分钟   |
| 大纲生成 | 5 次   | 每分钟   |
| 聊天对话 | 60 次  | 每分钟   |
| 查询操作 | 100 次 | 每分钟   |

---

## 🛠️ 开发工具和 SDK

### JavaScript SDK 示例

```javascript
class AIBackendClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  // 大纲生成
  async generateOutline(
    file,
    courseId,
    materialId,
    materialName,
    options = {}
  ) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("course_id", courseId);
    formData.append("course_material_id", materialId);
    formData.append("material_name", materialName);

    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined) {
        formData.append(key, value);
      }
    });

    const response = await fetch(`${this.baseUrl}/api/v1/outline/generate`, {
      method: "POST",
      body: formData,
    });

    return await response.json();
  }

  // 智能聊天
  async chat(
    conversationId,
    question,
    engineType = "condense_plus_context",
    filters = {}
  ) {
    const response = await fetch(`${this.baseUrl}/api/v1/conversation/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        question: question,
        chat_engine_type: engineType,
        ...filters,
      }),
    });

    return await response.json();
  }

  // 统一处理
  async processCourseMaterial(
    file,
    courseId,
    materialId,
    materialName,
    options = {}
  ) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("course_id", courseId);
    formData.append("course_material_id", materialId);
    formData.append("material_name", materialName);

    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined) {
        formData.append(key, value);
      }
    });

    const response = await fetch(
      `${this.baseUrl}/api/v1/course-materials/process`,
      {
        method: "POST",
        body: formData,
      }
    );

    return await response.json();
  }

  // 任务状态查询
  async getTaskStatus(taskId, endpoint = "course-materials") {
    const response = await fetch(
      `${this.baseUrl}/api/v1/${endpoint}/tasks/${taskId}/status`
    );
    return await response.json();
  }
}

// 使用示例
const client = new AIBackendClient();

// 处理课程材料
const result = await client.processCourseMaterial(
  fileInput.files[0],
  "CS101",
  "001",
  "Python基础",
  {
    include_refine: true,
    enable_rag_indexing: true,
  }
);

// 智能聊天
const chatResponse = await client.chat(
  "user123_session1",
  "Python中的变量是什么？",
  "condense_plus_context",
  { course_id: "CS101" }
);
```

### Python SDK 示例

```python
import requests
from typing import Optional, Dict, Any

class AIBackendClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def generate_outline(self, file_path: str, course_id: str,
                        material_id: str, material_name: str,
                        **options) -> Dict[str, Any]:
        """生成文档大纲"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'course_id': course_id,
                'course_material_id': material_id,
                'material_name': material_name,
                **options
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/outline/generate",
                files=files,
                data=data
            )

        return response.json()

    def chat(self, conversation_id: str, question: str,
             engine_type: str = "condense_plus_context",
             **filters) -> Dict[str, Any]:
        """智能聊天"""
        data = {
            "conversation_id": conversation_id,
            "question": question,
            "chat_engine_type": engine_type,
            **filters
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/conversation/chat",
            json=data
        )

        return response.json()

    def process_course_material(self, file_path: str, course_id: str,
                               material_id: str, material_name: str,
                               **options) -> Dict[str, Any]:
        """统一处理课程材料"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'course_id': course_id,
                'course_material_id': material_id,
                'material_name': material_name,
                **options
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/course-materials/process",
                files=files,
                data=data
            )

        return response.json()

# 使用示例
client = AIBackendClient()

# 处理课程材料
result = client.process_course_material(
    "python基础.md",
    "CS101",
    "001",
    "Python基础",
    include_refine=True,
    enable_rag_indexing=True
)

# 智能聊天
chat_response = client.chat(
    "user123_session1",
    "Python中的变量是什么？",
    "condense_plus_context",
    course_id="CS101"
)
```

---

## 📚 最佳实践

### 1. 文件上传最佳实践

- **文件格式**: 仅上传.md 或.txt 格式的文件
- **文件大小**: 控制在 10MB 以内
- **文件命名**: 使用有意义的文件名，避免特殊字符
- **内容质量**: 确保文档内容结构清晰，便于大纲生成

### 2. 任务管理最佳实践

- **轮询间隔**: 建议 2-5 秒轮询一次任务状态
- **超时处理**: 设置合理的超时时间（建议 5 分钟）
- **错误重试**: 对网络错误实施指数退避重试
- **状态缓存**: 缓存任务状态，避免频繁查询

### 3. 聊天对话最佳实践

- **会话管理**: 使用有意义的 conversation_id
- **引擎选择**: 根据需求选择合适的聊天引擎
- **过滤条件**: 合理使用 course_id 或 material_id 过滤
- **记忆管理**: 定期清理不需要的会话记录

### 4. 错误处理最佳实践

- **统一处理**: 实施统一的错误处理机制
- **用户友好**: 提供用户友好的错误提示
- **日志记录**: 记录详细的错误日志用于调试
- **优雅降级**: 在服务不可用时提供备选方案

---

## 📞 技术支持

### 获取帮助

- **API 文档**: 访问 `/docs` 获取交互式文档
- **健康检查**: 使用 `/health` 检查服务状态
- **错误日志**: 查看服务器日志获取详细错误信息
- **社区支持**: 通过 GitHub Issues 获取社区帮助

### 联系方式

- **项目地址**: https://github.com/your-username/rwai_fastapi
- **问题反馈**: https://github.com/your-username/rwai_fastapi/issues
- **邮箱支持**: your-email@example.com

---

**🚀 开始使用 AI 功能后端 API，构建您的智能应用！**
