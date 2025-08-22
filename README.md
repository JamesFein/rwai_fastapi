# AI 功能后端 - 智能教育助手

基于 FastAPI 构建的 AI 功能后端，提供完整的智能教育解决方案，包括文档大纲生成、RAG 问答、智能聊天等功能。

## 功能特性

### ✅ 已实现功能

#### 📝 文档大纲生成

- **智能大纲生成**: 上传 Markdown 或文本文件，生成结构化三层次大纲
- **两阶段处理**: 原始大纲生成 + 标题精简优化
- **课程化管理**: 基于 course_id 的文件组织和存储
- **材料唯一性**: 同一课程下 course_material_id 的唯一性验证

#### 🔍 RAG 问答系统

- **文档索引**: 基于 LlamaIndex 和 Qdrant 的向量数据库
- **智能检索**: 支持课程级别和材料级别的精确过滤
- **多引擎支持**: 检索增强模式和直接对话模式

#### 💬 智能聊天

- **对话记忆**: 基于 Redis 的会话管理
- **多模式聊天**: 支持文档问答和自由对话
- **实时响应**: 异步处理，高性能响应

#### 🎯 统一处理

- **一站式服务**: 文件上传、大纲生成、RAG 索引建立的统一 API
- **任务管理**: 完整的任务状态跟踪和查询
- **错误处理**: 自动清理和回滚机制

#### 🛡️ 安全与性能

- **文件安全**: 完整的文件上传验证和安全检查（仅支持 .md 和 .txt）
- **异步处理**: 基于 FastAPI 的高性能异步架构
- **性能监控**: 详细的性能指标和日志记录
- **CORS 支持**: 完整的跨域资源共享配置

## 快速开始

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

## 🚀 API 使用指南

### 1. 📝 文档大纲生成

#### 1.1 生成文档大纲

**端点**: `POST /api/v1/outline/generate`

**功能**: 上传文档文件并生成结构化大纲

**请求参数**:

```javascript
// FormData 格式
const formData = new FormData();
formData.append("file", fileInput.files[0]); // 必需：文件（.md/.txt）
formData.append("course_id", "CS101"); // 必需：课程ID
formData.append("course_material_id", "001"); // 必需：材料ID（课程内唯一）
formData.append("material_name", "Python基础"); // 必需：材料名称
formData.append("include_refine", "true"); // 可选：是否精简大纲（默认true）
formData.append("model_name", "gpt-4o-mini"); // 可选：指定模型
formData.append("custom_prompt", "请生成详细大纲"); // 可选：自定义提示词
```

**cURL 示例**:

```bash
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -F "file=@python基础.md" \
  -F "course_id=CS101" \
  -F "course_material_id=001" \
  -F "material_name=Python基础" \
  -F "include_refine=true"
```

**JavaScript 示例**:

```javascript
const generateOutline = async (file, courseId, materialId, materialName) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("course_id", courseId);
  formData.append("course_material_id", materialId);
  formData.append("material_name", materialName);
  formData.append("include_refine", true);

  const response = await fetch("/api/v1/outline/generate", {
    method: "POST",
    body: formData,
  });

  return await response.json();
};
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
  "created_at": "2024-08-14T10:30:00",
  "completed_at": "2024-08-14T10:30:15"
}
```

#### 1.2 查询任务状态

**端点**: `GET /api/v1/outline/task/{task_id}`

**JavaScript 示例**:

```javascript
const checkTaskStatus = async (taskId) => {
  const response = await fetch(`/api/v1/outline/task/${taskId}`);
  return await response.json();
};
```

#### 1.3 获取大纲文件

**端点**: `GET /api/v1/outline/file/{course_id}/{course_material_id}`

**JavaScript 示例**:

```javascript
const getOutlineFile = async (courseId, materialId) => {
  const response = await fetch(
    `/api/v1/outline/file/${courseId}/${materialId}`
  );
  return await response.json();
};
```

### 2. 🔍 RAG 文档索引

#### 2.1 建立文档索引

**端点**: `POST /api/v1/rag/index`

**功能**: 为上传的文档建立向量索引，用于后续的智能问答

**请求参数**:

```javascript
// FormData 格式
const formData = new FormData();
formData.append("file", fileInput.files[0]); // 必需：文件（.md/.txt）
formData.append("course_id", "CS101"); // 必需：课程ID
formData.append("course_material_id", "001"); // 必需：材料ID
formData.append("collection_name", "course_materials"); // 可选：集合名称
```

**JavaScript 示例**:

```javascript
const buildIndex = async (
  file,
  courseId,
  materialId,
  collectionName = null
) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("course_id", courseId);
  formData.append("course_material_id", materialId);
  if (collectionName) {
    formData.append("collection_name", collectionName);
  }

  const response = await fetch("/api/v1/rag/index", {
    method: "POST",
    body: formData,
  });

  return await response.json();
};
```

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

#### 2.2 获取集合列表

**端点**: `GET /api/v1/rag/collections`

**JavaScript 示例**:

```javascript
const getCollections = async () => {
  const response = await fetch("/api/v1/rag/collections");
  return await response.json();
};
```

### 3. 💬 智能聊天

#### 3.1 智能对话

**端点**: `POST /api/v1/conversation/chat`

**功能**: 与 AI 进行智能对话，支持基于文档的问答和自由聊天

**请求参数**:

```javascript
const chatRequest = {
  conversation_id: "user123_session1", // 必需：会话ID
  question: "Python中的变量是什么？", // 必需：用户问题
  chat_engine_type: "condense_plus_context", // 必需：引擎类型
  course_id: "CS101", // 可选：课程ID（与course_material_id二选一）
  course_material_id: "001", // 可选：材料ID（与course_id二选一）
  collection_name: "course_materials", // 可选：集合名称
};
```

**聊天引擎类型**:

- `condense_plus_context`: 检索增强模式，基于文档内容回答
- `simple`: 直接对话模式，不检索文档

**JavaScript 示例**:

```javascript
const chat = async (
  conversationId,
  question,
  engineType = "condense_plus_context",
  courseId = null,
  materialId = null
) => {
  const requestBody = {
    conversation_id: conversationId,
    question: question,
    chat_engine_type: engineType,
  };

  if (courseId) requestBody.course_id = courseId;
  if (materialId) requestBody.course_material_id = materialId;

  const response = await fetch("/api/v1/conversation/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  return await response.json();
};
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

#### 3.2 清除会话记录

**端点**: `DELETE /api/v1/conversation/conversations/{conversation_id}`

**JavaScript 示例**:

```javascript
const clearConversation = async (conversationId) => {
  const response = await fetch(
    `/api/v1/conversation/conversations/${conversationId}`,
    {
      method: "DELETE",
    }
  );
  return await response.json();
};
```

#### 3.3 获取可用引擎

**端点**: `GET /api/v1/conversation/engines`

**JavaScript 示例**:

```javascript
const getAvailableEngines = async () => {
  const response = await fetch("/api/v1/conversation/engines");
  return await response.json();
};
```

### 4. 🎯 统一课程材料处理

#### 4.1 一站式材料处理

**端点**: `POST /api/v1/course-materials/process`

**功能**: 统一处理课程材料，自动完成文件上传、大纲生成、RAG 索引建立的全流程

**请求参数**:

```javascript
// FormData 格式
const formData = new FormData();
formData.append("file", fileInput.files[0]); // 必需：文件（.md/.txt）
formData.append("course_id", "CS101"); // 必需：课程ID
formData.append("course_material_id", "001"); // 必需：材料ID
formData.append("material_name", "Python基础"); // 必需：材料名称
formData.append("custom_prompt", "请生成详细大纲"); // 可选：自定义提示词
formData.append("include_refine", "true"); // 可选：是否精简大纲
formData.append("model_name", "gpt-4o-mini"); // 可选：指定模型
formData.append("enable_rag_indexing", "true"); // 可选：是否建立RAG索引
formData.append("rag_collection_name", "course_materials"); // 可选：RAG集合名称
```

**JavaScript 示例**:

```javascript
const processCourseMaterial = async (
  file,
  courseId,
  materialId,
  materialName,
  options = {}
) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("course_id", courseId);
  formData.append("course_material_id", materialId);
  formData.append("material_name", materialName);

  // 可选参数
  if (options.customPrompt)
    formData.append("custom_prompt", options.customPrompt);
  if (options.includeRefine !== undefined)
    formData.append("include_refine", options.includeRefine);
  if (options.modelName) formData.append("model_name", options.modelName);
  if (options.enableRagIndexing !== undefined)
    formData.append("enable_rag_indexing", options.enableRagIndexing);
  if (options.ragCollectionName)
    formData.append("rag_collection_name", options.ragCollectionName);

  const response = await fetch("/api/v1/course-materials/process", {
    method: "POST",
    body: formData,
  });

  return await response.json();
};
```

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
  ]
}
```

#### 4.2 查询处理状态

**端点**: `GET /api/v1/course-materials/tasks/{task_id}/status`

**JavaScript 示例**:

```javascript
const getProcessingStatus = async (taskId) => {
  const response = await fetch(
    `/api/v1/course-materials/tasks/${taskId}/status`
  );
  return await response.json();
};
```

### 5. 🗂️ 课程管理

#### 5.1 删除指定材料

**端点**: `DELETE /api/v1/course-materials/{course_id}/{course_material_id}`

**功能**: 删除指定课程材料的所有数据，包括文件、大纲、RAG 索引等

**JavaScript 示例**:

```javascript
const deleteMaterial = async (courseId, materialId, options = {}) => {
  const params = new URLSearchParams({
    cleanup_files: options.cleanupFiles !== false,
    cleanup_rag_data: options.cleanupRagData !== false,
    cleanup_task_data: options.cleanupTaskData !== false,
  });

  const response = await fetch(
    `/api/v1/course-materials/${courseId}/${materialId}?${params}`,
    { method: "DELETE" }
  );
  return await response.json();
};
```

#### 5.2 删除整个课程

**端点**: `DELETE /api/v1/course/{course_id}`

**功能**: 删除整个课程及其所有材料和数据

**JavaScript 示例**:

```javascript
const deleteCourse = async (courseId) => {
  const response = await fetch(`/api/v1/course/${courseId}`, {
    method: "DELETE",
  });
  return await response.json();
};
```

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

## 🔧 前端集成示例

### 完整的课程材料处理流程

```javascript
class CourseMaterialManager {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  // 完整处理流程
  async processCourseMaterial(file, courseId, materialId, materialName) {
    try {
      // 1. 启动处理
      const processResponse = await this.processCourseMaterial(
        file,
        courseId,
        materialId,
        materialName,
        {
          includeRefine: true,
          enableRagIndexing: true,
        }
      );

      console.log("处理启动:", processResponse);

      // 2. 轮询状态直到完成
      const finalStatus = await this.waitForCompletion(processResponse.task_id);

      console.log("处理完成:", finalStatus);
      return finalStatus;
    } catch (error) {
      console.error("处理失败:", error);
      throw error;
    }
  }

  // 等待任务完成
  async waitForCompletion(taskId, maxWaitTime = 300000) {
    // 5分钟超时
    const startTime = Date.now();

    while (Date.now() - startTime < maxWaitTime) {
      const status = await this.getProcessingStatus(taskId);

      if (status.status === "completed") {
        return status;
      } else if (status.status === "failed") {
        throw new Error(`处理失败: ${status.error_message}`);
      }

      // 等待2秒后再次检查
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }

    throw new Error("处理超时");
  }

  // 智能聊天
  async startConversation(conversationId, courseId = null, materialId = null) {
    return {
      ask: async (question, engineType = "condense_plus_context") => {
        return await this.chat(
          conversationId,
          question,
          engineType,
          courseId,
          materialId
        );
      },
      clear: async () => {
        return await this.clearConversation(conversationId);
      },
    };
  }
}

// 使用示例
const manager = new CourseMaterialManager();

// 处理课程材料
const fileInput = document.getElementById("fileInput");
const file = fileInput.files[0];

manager
  .processCourseMaterial(file, "CS101", "001", "Python基础")
  .then((result) => {
    console.log("材料处理完成:", result);

    // 开始聊天
    const conversation = manager.startConversation("user123_session1", "CS101");
    return conversation.ask("Python中的变量是什么？");
  })
  .then((chatResponse) => {
    console.log("AI回答:", chatResponse.answer);
  })
  .catch((error) => {
    console.error("错误:", error);
  });
```

## 项目结构

```
ai-backend/
├── app/                          # 应用主目录
│   ├── api/                     # API 路由
│   │   └── v1/                  # API v1 版本
│   │       ├── __init__.py      # 路由注册
│   │       ├── outline.py       # 大纲生成 API
│   │       ├── rag.py           # RAG 索引 API
│   │       ├── chat.py          # 智能聊天 API
│   │       ├── conversation.py  # 智能对话 API
│   │       ├── course_materials.py # 统一材料处理 API
│   │       └── course.py        # 课程管理 API
│   ├── core/                    # 核心模块
│   │   ├── config.py           # 配置管理
│   │   ├── logging.py          # 日志配置
│   │   └── deps.py             # 依赖注入
│   ├── schemas/                 # 数据模型
│   │   ├── outline.py          # 大纲相关模型
│   │   ├── rag.py              # RAG 相关模型
│   │   └── course_materials.py # 课程材料模型
│   ├── services/                # 业务逻辑
│   │   ├── outline/            # 大纲生成服务
│   │   ├── rag/                # RAG 服务
│   │   └── course_material/    # 课程材料服务
│   ├── utils/                   # 工具函数
│   │   ├── fileio.py           # 文件操作
│   │   ├── idgen.py            # ID 生成
│   │   ├── timers.py           # 时间工具
│   │   └── validation.py       # 验证工具
│   ├── constants/               # 常量定义
│   │   └── paths.py            # 路径常量
│   ├── prompts/                 # 提示词模板
│   │   ├── outline_generation.md # 大纲生成提示词
│   │   ├── outline_refine.md     # 大纲精简提示词
│   │   └── chat/                 # 聊天提示词
│   ├── repositories/            # 数据访问层
│   │   └── rag_repository.py   # RAG 数据访问
│   └── main.py                 # 应用入口
├── data/                        # 数据目录
│   ├── uploads/                # 上传文件（按课程ID组织）
│   │   ├── CS101/              # 课程CS101的文件
│   │   │   ├── 001_Python基础.md
│   │   │   └── 002_Python进阶.txt
│   │   └── CS102/              # 课程CS102的文件
│   ├── outputs/                # 输出文件
│   │   └── outlines/           # 大纲输出（按课程ID组织）
│   │       ├── CS101/          # 课程CS101的大纲
│   │       │   ├── 001_Python基础.md
│   │       │   └── 002_Python进阶.md
│   │       └── CS102/          # 课程CS102的大纲
│   └── tmp/                    # 临时文件
├── frontend/                    # 前端应用（独立部署）
│   ├── index.html              # 主页面
│   ├── test-api.html           # API 测试页面
│   ├── css/                    # 样式文件
│   ├── js/                     # JavaScript 文件
│   │   ├── app.js              # 主应用逻辑
│   │   ├── api.js              # API 调用模块
│   │   └── chat.js             # 聊天功能
│   └── README.md               # 前端使用说明
├── tests/                       # 测试文件
├── dev_docs/                    # 开发文档
├── requirements.txt             # 依赖列表
├── .env.example                # 环境变量模板
└── README.md                   # 项目说明
```

---

## ⚠️ 错误处理和最佳实践

### 常见错误码

| 状态码 | 错误类型                | 说明                | 解决方案                         |
| ------ | ----------------------- | ------------------- | -------------------------------- |
| 400    | `validation_error`      | 请求参数验证失败    | 检查请求参数格式和必需字段       |
| 400    | `file_validation_error` | 文件验证失败        | 确认文件格式(.md/.txt)和大小限制 |
| 400    | `duplicate_material_id` | 课程材料 ID 重复    | 使用不同的 course_material_id    |
| 404    | `task_not_found`        | 任务不存在          | 检查 task_id 是否正确            |
| 404    | `file_not_found`        | 文件不存在          | 确认课程 ID 和材料 ID 是否正确   |
| 500    | `internal_error`        | 服务器内部错误      | 查看服务器日志，联系管理员       |
| 500    | `openai_api_error`      | OpenAI API 调用失败 | 检查 API 密钥和网络连接          |

### 前端错误处理示例

```javascript
class APIClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new APIError(response.status, errorData);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(0, {
        error: "network_error",
        message: "网络连接失败",
      });
    }
  }

  // 带重试的请求
  async requestWithRetry(endpoint, options = {}, maxRetries = 3) {
    let lastError;

    for (let i = 0; i <= maxRetries; i++) {
      try {
        return await this.request(endpoint, options);
      } catch (error) {
        lastError = error;

        // 只对网络错误和5xx错误重试
        if (error.status >= 400 && error.status < 500) {
          throw error;
        }

        if (i < maxRetries) {
          await new Promise((resolve) =>
            setTimeout(resolve, 1000 * Math.pow(2, i))
          );
        }
      }
    }

    throw lastError;
  }
}

class APIError extends Error {
  constructor(status, data) {
    super(data.message || "未知错误");
    this.status = status;
    this.error = data.error;
    this.detail = data.detail;
    this.task_id = data.task_id;
  }
}

// 使用示例
const client = new APIClient();

try {
  const result = await client.requestWithRetry("/api/v1/outline/generate", {
    method: "POST",
    body: formData,
  });
  console.log("成功:", result);
} catch (error) {
  if (error instanceof APIError) {
    switch (error.error) {
      case "validation_error":
        console.error("参数错误:", error.detail);
        break;
      case "duplicate_material_id":
        console.error("材料ID重复:", error.message);
        break;
      case "openai_api_error":
        console.error("AI服务错误:", error.message);
        break;
      default:
        console.error("API错误:", error.message);
    }
  } else {
    console.error("未知错误:", error);
  }
}
```

### 任务状态轮询最佳实践

```javascript
class TaskPoller {
  constructor(apiClient, options = {}) {
    this.apiClient = apiClient;
    this.pollInterval = options.pollInterval || 2000; // 2秒
    this.maxWaitTime = options.maxWaitTime || 300000; // 5分钟
    this.onProgress = options.onProgress || (() => {});
  }

  async waitForCompletion(taskId) {
    const startTime = Date.now();

    while (Date.now() - startTime < this.maxWaitTime) {
      try {
        const status = await this.apiClient.request(
          `/api/v1/course-materials/tasks/${taskId}/status`
        );

        // 调用进度回调
        this.onProgress(status);

        if (status.status === "completed") {
          return status;
        } else if (status.status === "failed") {
          throw new Error(`任务失败: ${status.error_message}`);
        }

        // 等待下次轮询
        await new Promise((resolve) => setTimeout(resolve, this.pollInterval));
      } catch (error) {
        if (error instanceof APIError && error.status === 404) {
          throw new Error("任务不存在");
        }
        throw error;
      }
    }

    throw new Error("任务超时");
  }
}

// 使用示例
const poller = new TaskPoller(client, {
  onProgress: (status) => {
    console.log(
      `进度: ${status.progress_percentage}% - ${status.current_step}`
    );
    updateProgressBar(status.progress_percentage);
  },
});

const result = await poller.waitForCompletion(taskId);
```

## 配置说明

主要配置项（在 `.env` 文件中设置）：

```env
# OpenAI API 配置
API_KEY=your_openai_api_key                    # 必需：OpenAI API密钥
BASE_URL=https://api.openai.com/v1             # 可选：API基础URL
OUTLINE_MODEL=gpt-4o-mini                      # 可选：大纲生成模型
REFINE_MODEL=gpt-4o-mini                       # 可选：大纲精简模型

# RAG 配置
QDRANT_URL=http://localhost:6333               # 可选：Qdrant向量数据库URL
QDRANT_API_KEY=                                # 可选：Qdrant API密钥
REDIS_URL=redis://localhost:6379               # 可选：Redis连接URL
EMBEDDING_MODEL=text-embedding-3-small         # 可选：嵌入模型

# 服务配置
HOST=0.0.0.0                                  # 服务监听地址
PORT=8000                                     # 服务端口
DEBUG=true                                    # 调试模式

# 文件配置
MAX_FILE_SIZE=10485760                        # 最大文件大小（10MB）
ALLOWED_EXTENSIONS=.md,.txt                   # 允许的文件扩展名

# 日志配置
LOG_LEVEL=INFO                                # 日志级别
LOG_FORMAT=json                               # 日志格式
```

---

## 🎯 使用场景和工作流程

### 场景 1：课程材料管理

**适用于**: 教育机构、在线课程平台

```javascript
// 1. 批量上传课程材料
const materials = [
  { file: "python基础.md", id: "001", name: "Python基础" },
  { file: "python进阶.md", id: "002", name: "Python进阶" },
  { file: "python实战.md", id: "003", name: "Python实战" },
];

for (const material of materials) {
  const result = await processCourseMaterial(
    material.file,
    "CS101",
    material.id,
    material.name
  );
  console.log(`${material.name} 处理完成`);
}

// 2. 学生问答
const conversation = await startConversation("student123", "CS101");
const answer = await conversation.ask("Python中的变量是什么？");
console.log("AI回答:", answer.answer);
```

### 场景 2：文档知识库

**适用于**: 企业知识管理、技术文档

```javascript
// 1. 建立知识库
const docs = ["API文档.md", "用户手册.md", "开发指南.md"];
for (const doc of docs) {
  await processCourseMaterial(doc, "DOCS", generateId(), doc);
}

// 2. 智能检索
const answer = await chat(
  "session1",
  "如何使用API？",
  "condense_plus_context",
  "DOCS"
);
```

### 场景 3：个人学习助手

**适用于**: 个人学习、研究笔记

```javascript
// 1. 上传学习材料
await processCourseMaterial(
  "机器学习笔记.md",
  "ML_STUDY",
  "001",
  "机器学习基础"
);

// 2. 生成学习大纲
const outline = await getOutlineFile("ML_STUDY", "001");

// 3. 智能问答
const qa = await chat(
  "my_study",
  "什么是梯度下降？",
  "condense_plus_context",
  null,
  "001"
);
```

---

## 📊 性能和限制

### 性能指标

| 操作     | 平均响应时间 | 并发支持 | 备注                 |
| -------- | ------------ | -------- | -------------------- |
| 文件上传 | < 1 秒       | 50+      | 取决于文件大小       |
| 大纲生成 | 10-30 秒     | 10+      | 取决于文档长度和模型 |
| RAG 索引 | 5-15 秒      | 20+      | 取决于文档复杂度     |
| 智能问答 | 2-8 秒       | 100+     | 取决于检索范围       |

### 系统限制

| 项目     | 限制      | 说明                   |
| -------- | --------- | ---------------------- |
| 文件大小 | 10MB      | 可在配置中调整         |
| 文件格式 | .md, .txt | 纯文本格式             |
| 并发任务 | 50 个     | 大纲生成任务           |
| 会话数量 | 1000 个   | Redis 内存限制         |
| 向量维度 | 1536      | text-embedding-3-small |

### 扩展建议

1. **高并发场景**: 使用负载均衡和多实例部署
2. **大文件处理**: 实现文件分块上传
3. **多格式支持**: 添加 PDF、Word 等格式解析
4. **缓存优化**: 使用 Redis 缓存频繁查询结果
5. **监控告警**: 集成 Prometheus 和 Grafana

---

## 🔧 开发和部署

### 本地开发

```bash
# 1. 克隆项目
git clone <repository-url>
cd rwai_fastapi

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 5. 启动服务
python -m app.main
```

### Docker 部署

```bash
# 构建镜像
docker build -t ai-backend .

# 运行容器
docker run -d \
  --name ai-backend \
  -p 8000:8000 \
  --env-file .env \
  ai-backend
```

### 生产环境部署

```bash
# 使用 Gunicorn + Uvicorn
pip install gunicorn
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 依赖服务

```yaml
# docker-compose.yml
version: "3.8"
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  ai-backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - qdrant
      - redis
    env_file:
      - .env

volumes:
  qdrant_data:
  redis_data:
```

---

## 🛠️ 故障排除

### 常见问题和解决方案

#### 1. API 调用相关

**问题**: OpenAI API 调用失败

```
Error: openai_api_error - API调用失败
```

**解决方案**:

- 检查 `.env` 文件中的 `API_KEY` 是否正确
- 确认网络连接正常，可以访问 OpenAI API
- 检查 API 配额是否用完
- 查看服务器日志获取详细错误信息

**问题**: Qdrant 连接失败

```
Error: 无法连接到向量数据库
```

**解决方案**:

- 确认 Qdrant 服务正在运行：`docker ps | grep qdrant`
- 检查 `QDRANT_URL` 配置是否正确
- 验证网络连接：`curl http://localhost:6333/health`

#### 2. 文件处理相关

**问题**: 文件上传失败

```
Error: file_validation_error - 不支持的文件类型
```

**解决方案**:

- 确认文件格式为 `.md` 或 `.txt`
- 检查文件大小是否超过 10MB 限制
- 验证文件内容不为空

**问题**: 课程材料 ID 重复

```
Error: duplicate_material_id - 课程材料ID已存在
```

**解决方案**:

- 使用不同的 `course_material_id`
- 或者先删除现有材料：`DELETE /api/v1/course-materials/{course_id}/{course_material_id}`

#### 3. 服务启动相关

**问题**: 端口被占用

```
Error: [Errno 98] Address already in use
```

**解决方案**:

```bash
# 查找占用端口的进程
lsof -i :8000
# 或
netstat -tulpn | grep 8000

# 终止进程
kill -9 <PID>

# 或使用不同端口
PORT=8001 python -m app.main
```

**问题**: 环境变量未加载

```
Error: API_KEY is required
```

**解决方案**:

- 确认 `.env` 文件存在且格式正确
- 检查环境变量名称拼写
- 手动设置环境变量：`export API_KEY=your_key`

### 调试技巧

#### 1. 启用详细日志

```bash
# 设置调试模式
DEBUG=true LOG_LEVEL=DEBUG python -m app.main
```

#### 2. 查看实时日志

```bash
# 跟踪日志文件
tail -f logs/app.log

# 或使用 Docker
docker logs -f ai-backend
```

#### 3. API 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 测试文件上传
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -F "file=@test.md" \
  -F "course_id=TEST" \
  -F "course_material_id=001" \
  -F "material_name=测试文件"
```

#### 4. 数据库检查

```bash
# 检查 Qdrant 集合
curl http://localhost:6333/collections

# 检查 Redis 连接
redis-cli ping
```

---

## 📚 开发指南

### 添加新的 API 端点

1. **定义数据模型** (`app/schemas/`)

```python
# app/schemas/new_feature.py
from pydantic import BaseModel, Field

class NewFeatureRequest(BaseModel):
    name: str = Field(..., description="功能名称")
    description: str = Field(..., description="功能描述")

class NewFeatureResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
```

2. **实现业务逻辑** (`app/services/`)

```python
# app/services/new_feature/new_feature_service.py
from ...schemas.new_feature import NewFeatureRequest, NewFeatureResponse

class NewFeatureService:
    async def process(self, request: NewFeatureRequest) -> NewFeatureResponse:
        # 实现业务逻辑
        return NewFeatureResponse(
            success=True,
            message="处理成功"
        )

new_feature_service = NewFeatureService()
```

3. **添加 API 路由** (`app/api/v1/`)

```python
# app/api/v1/new_feature.py
from fastapi import APIRouter, Depends
from ...schemas.new_feature import NewFeatureRequest, NewFeatureResponse
from ...services.new_feature.new_feature_service import new_feature_service

router = APIRouter(prefix="/new-feature", tags=["新功能"])

@router.post("/process", response_model=NewFeatureResponse)
async def process_new_feature(request: NewFeatureRequest):
    return await new_feature_service.process(request)
```

4. **注册路由** (`app/api/v1/__init__.py`)

```python
from .new_feature import router as new_feature_router

api_router.include_router(new_feature_router)
```

### 测试开发

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx pytest-mock

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_outline.py -v

# 生成覆盖率报告
pytest --cov=app tests/
```

### 代码质量

```bash
# 安装代码质量工具
pip install black isort flake8 mypy

# 代码格式化
black app/ tests/
isort app/ tests/

# 代码检查
flake8 app/
mypy app/
```

---

## 📖 更新日志

### v1.2.0 (2024-08-22)

- ✨ 新增统一课程材料处理 API
- ✨ 新增智能聊天和对话功能
- ✨ 新增 RAG 文档索引和检索
- ✨ 新增课程管理功能
- 🔧 优化错误处理和日志记录
- 📚 完善 API 文档和使用示例

### v1.1.0 (2024-08-14)

- ✨ 新增大纲生成功能
- ✨ 新增文件上传和验证
- ✨ 新增任务状态跟踪
- 🔧 实现课程化文件管理
- 📚 添加详细的 API 文档

### v1.0.0 (2024-08-01)

- 🎉 项目初始版本
- ✨ 基础 FastAPI 框架搭建
- 🔧 环境配置和依赖管理

---

## 🤝 贡献指南

### 贡献流程

1. **Fork 项目**

   ```bash
   git clone https://github.com/your-username/rwai_fastapi.git
   cd rwai_fastapi
   ```

2. **创建功能分支**

   ```bash
   git checkout -b feature/new-feature
   ```

3. **开发和测试**

   ```bash
   # 安装开发依赖
   pip install -r requirements-dev.txt

   # 运行测试
   pytest

   # 代码检查
   black app/ && isort app/ && flake8 app/
   ```

4. **提交更改**

   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

5. **推送和创建 PR**
   ```bash
   git push origin feature/new-feature
   # 在 GitHub 上创建 Pull Request
   ```

### 代码规范

- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 遵循 PEP 8 编码规范
- 添加类型注解
- 编写单元测试
- 更新相关文档

### 提交信息规范

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- **项目地址**: https://github.com/your-username/rwai_fastapi
- **问题反馈**: https://github.com/your-username/rwai_fastapi/issues
- **邮箱**: your-email@example.com

---

## 🙏 致谢

感谢以下开源项目的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [LlamaIndex](https://www.llamaindex.ai/) - 数据框架和 RAG 引擎
- [Qdrant](https://qdrant.tech/) - 向量数据库
- [Redis](https://redis.io/) - 内存数据库
- [OpenAI](https://openai.com/) - AI 模型服务

---

**🚀 开始使用 AI 功能后端，构建您的智能教育应用！**
