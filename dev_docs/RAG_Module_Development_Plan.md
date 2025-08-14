# RAG 模块开发计划

## 项目概述

基于当前 FastAPI 项目结构和 LlamaIndex ChatEngines 教程，开发一个完整的 RAG（检索增强生成）模块，支持文档索引建立、向量存储持久化和智能问答功能。

### 核心功能

1. **文档索引建立**：支持 MD 文件上传，自动分块和向量化存储到 Qdrant v1.14.1
2. **双模式问答**：
   - **检索模式（query）**：基于 condense_question ChatEngine，检索知识库回答问题
   - **直接聊天模式（chat）**：基于 simple ChatEngine，不检索知识库，直接对话
3. **记忆管理**：使用 ChatSummaryMemoryBuffer 管理对话历史，前端 localStorage 持久化

## 开发环境要求

- Python 3.11
- FastAPI 0.116.1
- LlamaIndex 0.13.0
- Qdrant v1.14.1 向量数据库
- OpenAI API

## 第一阶段：环境准备和依赖配置

### 1.1 更新依赖包

- 在 requirements.txt 中添加缺失的 LlamaIndex 相关包：
  - llama-index-llms-openai>=0.3.0,<0.4
  - llama-index-embeddings-openai>=0.3.0,<0.4
  - llama-index-retrievers-bm25>=0.2.0,<0.3
  - llama-index-vector-stores-qdrant>=0.3.0,<0.4

### 1.2 环境变量配置

- 在.env 文件中添加 RAG 相关配置：
  - RAG_EMBED_MODEL=text-embedding-3-small
  - RAG_LLM_MODEL=gpt-4o-mini
  - QDRANT_URL=http://localhost:6333
  - QDRANT_GRPC_PORT=6334
  - QDRANT_COLLECTION_NAME=course_materials
  - QDRANT_PREFER_GRPC=True

### 1.3 Qdrant 数据库部署

- 使用 Docker 部署 Qdrant v1.14.1，同时暴露 HTTP 和 gRPC 端口
- Docker 命令：`docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:v1.14.1`
- 端口说明：
  - 6333：HTTP REST API 端口
  - 6334：gRPC API 端口（推荐用于 FastAPI 生产环境）
- 验证 Qdrant 服务可用性

## 第二阶段：核心配置和基础设施

### 2.1 更新核心配置

- 在 app/core/config.py 中添加 RAG 相关配置类
- 配置 LlamaIndex Settings 全局设置
- 添加 Qdrant 客户端配置（支持 gRPC 连接）
- 配置 gRPC 连接参数：host、grpc_port=6334、prefer_grpc=True

### 2.2 创建 RAG 数据模型

- 在 app/schemas/rag.py 中定义：
  - IndexRequest：索引建立请求模型
  - QueryRequest：问答查询请求模型（支持检索模式和直接聊天模式）
  - QueryResponse：问答响应模型
  - ChatMemory：聊天记忆模型

### 2.3 创建存储仓库

- 在 app/repositories/rag_repository.py 中实现：
  - Qdrant 向量存储操作
  - 文档元数据管理
  - 索引状态跟踪

## 第三阶段：RAG 服务层开发

### 3.1 创建 RAG 服务核心

- 在 app/services/rag_service.py 中实现：
  - 文档加载和预处理
  - 文本分块（SentenceSplitter，chunk_size=512，chunk_overlap=50）
  - 向量索引建立
  - Qdrant 持久化存储

### 3.2 实现 ChatEngine 功能

- 基于 LlamaIndex_ChatEngines_SharedMemory_Tutorial.ipynb 实现：
  - 检索模式：condense_question ChatEngine（基于向量检索）
  - 直接聊天模式：simple ChatEngine（不检索知识库）
  - ChatSummaryMemoryBuffer 共享记忆
  - 自定义摘要提示词支持

### 3.3 创建提示词管理

- 在 app/prompts/目录下创建 txt 格式提示词文件：
  - rag_system_prompt.txt：RAG 系统提示词
  - chat_summary_prompt.txt：聊天摘要提示词
  - condense_question_prompt.txt：问题压缩提示词

## 第四阶段：API 接口开发

### 4.1 创建 RAG API 路由

- 在 app/api/v1/rag.py 中实现：
  - POST /api/v1/rag/index：建立文档索引
  - POST /api/v1/rag/query：RAG 问答查询
  - GET /api/v1/rag/collections：获取集合列表
  - DELETE /api/v1/rag/collections/{collection_id}：删除集合

### 4.2 实现索引建立接口

- 接收 MD 文件上传
- 提取 course_id、course_material_id、course_material_name 元数据
- 执行文档分块和向量化
- 存储到 Qdrant 向量数据库

### 4.3 实现问答查询接口

- 支持检索模式（condense_question）和直接聊天模式（simple）
- 接收前端传递的聊天历史记忆
- 返回答案和更新后的记忆状态

## 第五阶段：工具脚本开发

### 5.1 创建索引构建脚本

- 在 scripts/build_rag_index.py 中实现：
  - 批量文档索引建立
  - 索引状态监控
  - 错误处理和重试机制

### 5.2 创建数据管理脚本

- 在 scripts/rag_data_manager.py 中实现：
  - 向量数据库备份
  - 索引重建工具
  - 数据清理工具

## 第六阶段：测试开发

### 6.1 单元测试

- 在 tests/test_rag.py 中实现：
  - RAG 服务功能测试
  - 向量存储操作测试
  - ChatEngine 功能测试

### 6.2 集成测试

- API 接口集成测试
- 端到端 RAG 流程测试
- 性能基准测试

## 第七阶段：优化和部署

### 7.1 性能优化

- 向量检索性能调优
- 内存使用优化
- 并发处理优化

### 7.2 监控和日志

- 添加 RAG 操作日志
- 性能指标监控
- 错误追踪和报警

### 7.3 文档和部署

- API 文档更新
- 部署指南编写
- 运维手册制作

## 关键技术要点

### Qdrant gRPC 连接配置

1. **gRPC 优势**：

   - 比 HTTP REST API 性能更高，特别适合大批量向量上传
   - 支持异步操作，提升 FastAPI 应用性能
   - 二进制协议，传输效率更高

2. **连接配置要点**：

   - 使用端口 6334 进行 gRPC 连接
   - 设置 prefer_grpc=True 优先使用 gRPC
   - 支持同步和异步客户端
   - 在 FastAPI 中使用单例模式避免重复创建连接

3. **LlamaIndex 集成**：
   - QdrantVectorStore 支持 gRPC 连接
   - 可同时配置同步和异步客户端
   - 支持混合搜索（dense + sparse vectors）

### 文档处理流程

1. 使用 SimpleDirectoryReader 加载 MD 文件
2. 为每个文档添加 course_id、course_material_id、course_material_name 元数据
3. 使用 SentenceSplitter 进行文本分块（chunk_size=512，chunk_overlap=50）
4. 生成向量嵌入并存储到 Qdrant v1.14.1

### 双模式 ChatEngine 实现

1. **检索模式（query）**：

   - 使用 condense_question ChatEngine
   - 基于向量检索相关文档片段
   - 结合上下文生成答案
   - 适用于知识问答场景

2. **直接聊天模式（chat）**：

   - 使用 simple ChatEngine
   - 不检索知识库，直接对话
   - 基于 LLM 的通用对话能力
   - 适用于闲聊和通用问题

3. **共享记忆管理**：
   - 使用 ChatSummaryMemoryBuffer 管理聊天记忆
   - 前端通过 localStorage 持久化聊天历史
   - 支持自定义摘要提示词

### 数据持久化

1. Qdrant v1.14.1 向量数据库存储文档向量
2. 元数据包含 course_id、course_material_id、course_material_name
3. 聊天记忆通过前端 localStorage 持久化
4. 支持多用户隔离和数据安全

## 预期交付物

1. 完整的 RAG 模块代码
2. API 接口文档
3. 单元测试和集成测试
4. 部署和运维文档
5. 性能基准报告

## 风险和注意事项

1. Qdrant 数据库连接稳定性
2. OpenAI API 调用频率限制
3. 大文档处理内存占用
4. 向量检索性能优化
5. 多用户并发访问处理
6. 数据安全和隐私保护

## 详细实现步骤

### 第一阶段详细步骤

#### 1.1.1 更新 requirements.txt

在现有依赖基础上添加：

- llama-index-llms-openai>=0.3.0,<0.4
- llama-index-embeddings-openai>=0.3.0,<0.4
- llama-index-retrievers-bm25>=0.2.0,<0.3
- llama-index-vector-stores-qdrant>=0.3.0,<0.4

#### 1.1.2 创建.env 配置

RAG 模块配置项：

- RAG_EMBED_MODEL=text-embedding-3-small
- RAG_LLM_MODEL=gpt-4o-mini
- QDRANT_URL=http://localhost:6333
- QDRANT_GRPC_PORT=6334
- QDRANT_PREFER_GRPC=True
- QDRANT_COLLECTION_NAME=course_materials
- RAG_CHUNK_SIZE=512
- RAG_CHUNK_OVERLAP=50
- RAG_TOP_K=5

#### 1.1.3 Qdrant 部署验证

- 启动 Qdrant 容器
- 测试连接性
- 创建初始集合

### 第二阶段详细步骤

#### 2.1.1 更新 app/core/config.py

- 添加 RAGSettings 类
- 配置 Qdrant 连接参数
- 设置 LlamaIndex 全局配置

#### 2.1.2 创建 app/schemas/rag.py

- IndexRequest：文件上传和元数据
- QueryRequest：查询文本和聊天模式
- QueryResponse：答案和记忆状态
- DocumentMetadata：文档元数据结构

#### 2.1.3 创建 app/repositories/rag_repository.py

- QdrantRepository 类
- 向量存储 CRUD 操作
- 集合管理功能

### 第三阶段详细步骤

#### 3.1.1 创建 app/services/rag_service.py

- RAGService 主服务类
- 文档处理 pipeline
- 索引建立流程

#### 3.1.2 实现 ChatEngine 服务

- CondenseQuestionChatEngine 配置
- SimpleChatEngine 配置
- ChatSummaryMemoryBuffer 管理

#### 3.1.3 创建提示词文件

- app/prompts/rag_system_prompt.txt
- app/prompts/chat_summary_prompt.txt
- app/prompts/condense_question_prompt.txt

### 第四阶段详细步骤

#### 4.1.1 创建 app/api/v1/rag.py

- 路由定义和依赖注入
- 请求验证和错误处理
- 响应格式标准化

#### 4.1.2 实现索引 API

- 文件上传处理
- 异步索引建立
- 进度状态跟踪

#### 4.1.3 实现查询 API

- 模式选择逻辑
- 记忆状态管理
- 流式响应支持

### 第五阶段详细步骤

#### 5.1.1 创建 scripts/build_rag_index.py

- 命令行参数解析
- 批量文档处理
- 进度显示和日志

#### 5.1.2 创建 scripts/rag_data_manager.py

- 数据备份功能
- 索引重建工具
- 清理和维护脚本

### 第六阶段详细步骤

#### 6.1.1 创建 tests/test_rag.py

- 单元测试用例
- Mock 对象配置
- 测试数据准备

#### 6.1.2 集成测试

- API 端点测试
- 数据库集成测试
- 性能基准测试

## 关键技术实现要点

### RAG 服务核心结构

RAGService 主要包含以下功能：

- 初始化 Qdrant 客户端、LLM 和嵌入模型
- 文档分块和向量化处理
- RAG 查询处理逻辑

### ChatEngine 配置要点

- 检索模式：使用 condense_question 模式，结合向量检索
- 直接聊天模式：使用 simple 模式，不检索知识库
- 共享记忆：使用 ChatSummaryMemoryBuffer 管理对话历史

## 数据流程图

文档上传 → 文本分块 → 向量化 → Qdrant 存储
↓
用户查询 → 向量检索 → 上下文构建 → LLM 生成 → 返回答案
↓
记忆更新 → 前端 localStorage → 下次查询使用

## 配置文件示例

### app/core/config.py 扩展

RAGSettings 配置类包含：

- Qdrant 配置：URL、gRPC 端口、连接偏好和集合名称
- LlamaIndex 配置：嵌入模型、LLM 模型、分块参数
- ChatEngine 配置：记忆 token 限制、摘要模板
- gRPC 连接配置：host、grpc_port=6334、prefer_grpc=True

### 提示词文件内容

#### app/prompts/rag_system_prompt.txt

专业学习助手系统提示词，包含：

- 基于课程材料回答问题的原则
- 上下文信息和问题的占位符
- 回答格式要求

#### app/prompts/chat_summary_prompt.txt

聊天记忆摘要提示词，用于：

- 总结对话历史内容
- 保留关键信息和上下文

#### app/prompts/condense_question_prompt.txt

问题压缩提示词，用于：

- 将问题重新表述为独立问题
- 包含必要的上下文信息

## API 接口设计

### 索引建立接口

POST /api/v1/rag/index

- 接收 MD 文件上传和元数据
- 返回索引建立结果和统计信息

### RAG 查询接口

POST /api/v1/rag/query

- 支持检索模式（query）和直接聊天模式（chat）
- 接收问题、模式选择、课程 ID 和聊天历史
- 返回答案、来源信息和更新后的聊天历史

## 部署和运维

### Docker Compose 配置

使用 Docker Compose 部署 Qdrant v1.14.1 和 FastAPI 服务：

- Qdrant 服务：端口 6333（HTTP）和 6334（gRPC），数据持久化
- FastAPI 服务：端口 8000，依赖 Qdrant 服务，使用 gRPC 连接
- 推荐在生产环境中使用 gRPC 连接以获得更好的性能

### 监控指标

- 索引建立成功率
- 查询响应时间
- 向量检索准确率
- 内存和 CPU 使用率
- Qdrant 连接状态
- gRPC 连接性能指标
- 向量上传吞吐量
