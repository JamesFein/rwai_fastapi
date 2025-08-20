# RAG服务 API v2 文档

## 概述

RAG服务 API v2 是重构后的新版本API，提供了更清晰的接口设计和更好的性能。

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v2
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 认证

当前版本暂不需要认证，后续版本将添加API密钥认证。

## 错误处理

所有API错误都遵循标准HTTP状态码：

- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `422`: 数据验证错误
- `500`: 服务器内部错误

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```

## 文档管理 API

### 1. 建立文档索引

**端点**: `POST /api/v1/rag/v2/index`

**描述**: 上传文档并建立向量索引

**请求格式**: `multipart/form-data`

**参数**:
- `file` (文件): 要索引的文档文件 (.md, .txt)
- `course_id` (字符串): 课程ID
- `course_material_id` (字符串): 课程材料ID
- `course_material_name` (字符串): 课程材料名称
- `collection_name` (字符串, 可选): 集合名称

**响应示例**:
```json
{
  "success": true,
  "message": "索引建立成功",
  "document_count": 1,
  "chunk_count": 3,
  "processing_time": 5.2,
  "collection_name": "course_materials"
}
```

### 2. 获取集合列表

**端点**: `GET /api/v1/rag/v2/collections`

**描述**: 获取所有可用的文档集合

**响应示例**:
```json
[
  {
    "name": "course_materials",
    "vectors_count": 150,
    "indexed_only": false,
    "payload_schema": {}
  }
]
```

### 3. 获取集合信息

**端点**: `GET /api/v1/rag/v2/collections/{collection_name}`

**描述**: 获取指定集合的详细信息

**响应示例**:
```json
{
  "name": "course_materials",
  "vectors_count": 150,
  "indexed_only": false,
  "payload_schema": {}
}
```

### 4. 删除集合

**端点**: `DELETE /api/v1/rag/v2/collections/{collection_name}`

**描述**: 删除指定的文档集合

**响应示例**:
```json
{
  "success": true,
  "message": "集合删除成功",
  "collection_name": "course_materials"
}
```

### 5. 按课程删除文档

**端点**: `DELETE /api/v1/rag/v2/documents/course/{course_id}`

**描述**: 删除指定课程的所有文档

**参数**:
- `collection_name` (查询参数, 可选): 集合名称

**响应示例**:
```json
{
  "success": true,
  "message": "课程文档删除成功",
  "course_id": "python_course",
  "deleted_count": 25
}
```

### 6. 按材料删除文档

**端点**: `DELETE /api/v1/rag/v2/documents/material/{course_id}/{material_id}`

**描述**: 删除指定课程材料的文档

**响应示例**:
```json
{
  "success": true,
  "message": "课程材料文档删除成功",
  "course_id": "python_course",
  "material_id": "chapter1",
  "deleted_count": 5
}
```

### 7. 统计文档数量

**端点**: `GET /api/v1/rag/v2/collections/{collection_name}/count`

**描述**: 统计指定集合中的文档数量

**响应示例**:
```json
{
  "collection_name": "course_materials",
  "document_count": 150
}
```

### 8. 健康检查

**端点**: `GET /api/v1/rag/v2/health`

**描述**: 检查RAG服务健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "version": "v2",
  "timestamp": "2025-08-20T21:30:00",
  "services": {
    "qdrant": "connected",
    "redis": "connected"
  }
}
```

## 对话管理 API

### 1. 智能聊天

**端点**: `POST /api/v1/conversation/v2/chat`

**描述**: 进行智能对话，支持两种模式

**请求体**:
```json
{
  "conversation_id": "user_session_123",
  "question": "什么是Python？",
  "chat_engine_type": "condense_plus_context",
  "course_id": "python_course",
  "course_material_id": "chapter1",
  "collection_name": "course_materials"
}
```

**参数说明**:
- `conversation_id` (必需): 对话会话ID
- `question` (必需): 用户问题
- `chat_engine_type` (必需): 聊天引擎类型
  - `simple`: 直接对话模式
  - `condense_plus_context`: 检索增强模式
- `course_id` (可选): 课程ID，用于过滤
- `course_material_id` (可选): 课程材料ID，用于过滤
- `collection_name` (可选): 集合名称

**响应示例**:
```json
{
  "answer": "Python是一种高级编程语言...",
  "sources": [
    {
      "course_id": "python_course",
      "course_material_id": "chapter1",
      "course_material_name": "Python基础",
      "chunk_text": "Python是一种解释型语言...",
      "score": 0.95
    }
  ],
  "conversation_id": "user_session_123",
  "chat_engine_type": "condense_plus_context",
  "filter_info": "course_id = python_course",
  "processing_time": 2.5
}
```

### 2. 获取可用引擎

**端点**: `GET /api/v1/conversation/v2/engines`

**描述**: 获取所有可用的聊天引擎信息

**响应示例**:
```json
{
  "version": "v2",
  "engines": [
    {
      "type": "condense_plus_context",
      "name": "检索增强模式",
      "description": "基于文档内容的智能问答",
      "features": ["向量检索", "上下文整合", "来源追踪"],
      "use_cases": ["课程内容问答", "文档知识查询"]
    },
    {
      "type": "simple",
      "name": "直接对话模式",
      "description": "与AI直接对话，不检索文档",
      "features": ["快速响应", "对话记忆"],
      "use_cases": ["一般性聊天", "创意讨论"]
    }
  ]
}
```

### 3. 清除对话

**端点**: `DELETE /api/v1/conversation/v2/conversations/{conversation_id}`

**描述**: 清除指定的对话记录

**响应示例**:
```json
{
  "success": true,
  "message": "对话清除成功",
  "conversation_id": "user_session_123"
}
```

### 4. 获取对话状态

**端点**: `GET /api/v1/conversation/v2/conversations/{conversation_id}/status`

**描述**: 获取对话的状态信息

**响应示例**:
```json
{
  "conversation_id": "user_session_123",
  "exists": true,
  "message_count": 5,
  "last_activity": "2025-08-20T21:30:00"
}
```

### 5. 获取对话配置

**端点**: `GET /api/v1/conversation/v2/config`

**描述**: 获取对话服务的配置信息

**响应示例**:
```json
{
  "memory_management": "Redis-based chat store",
  "prompt_templates": "File-based templates",
  "vector_search": "Qdrant vector database",
  "llm_backend": "OpenAI compatible API"
}
```

### 6. 健康检查

**端点**: `GET /api/v1/conversation/v2/health`

**描述**: 检查对话服务健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "version": "v2",
  "timestamp": "2025-08-20T21:30:00",
  "services": {
    "redis": "connected",
    "llm_api": "available"
  }
}
```

## 使用示例

### 完整工作流程

1. **上传文档**:
```bash
curl -X POST "http://localhost:8000/api/v1/rag/v2/index" \
  -F "file=@document.md" \
  -F "course_id=python_course" \
  -F "course_material_id=chapter1" \
  -F "course_material_name=Python基础"
```

2. **进行对话**:
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/v2/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user_123",
    "question": "什么是Python？",
    "chat_engine_type": "condense_plus_context",
    "course_id": "python_course"
  }'
```

3. **清理资源**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/conversation/v2/conversations/user_123"
curl -X DELETE "http://localhost:8000/api/v1/rag/v2/documents/course/python_course"
```

## 版本变更

### v2 新特性

1. **模块化设计**: 清晰分离文档管理和对话管理
2. **统一配置**: 集中的配置管理
3. **更好的错误处理**: 详细的错误信息和日志
4. **性能优化**: 改进的缓存和连接管理
5. **扩展性**: 更容易添加新功能

### 从 v1 迁移

请参考 `迁移指南.md` 了解详细的迁移步骤。
