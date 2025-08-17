# RAG模块使用说明

## 概述

RAG（检索增强生成）模块已成功开发完成，支持文档索引建立、向量存储持久化和智能问答功能。

## 功能特性

### 核心功能
1. **文档索引建立**：支持MD文件上传，自动分块和向量化存储到Qdrant
2. **双模式问答**：
   - **检索模式（query）**：基于向量检索回答问题
   - **直接聊天模式（chat）**：不检索知识库，直接对话
3. **记忆管理**：使用ChatSummaryMemoryBuffer管理对话历史

### 技术栈
- **LlamaIndex 0.13.0**：文档处理和RAG框架
- **Qdrant v1.14.1**：向量数据库（支持gRPC连接）
- **OpenAI API**：嵌入模型和语言模型
- **FastAPI**：API接口框架

## 快速开始

### 1. 环境准备

确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

确保Qdrant服务正在运行：
```bash
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant:v1.14.1
```

### 2. 配置环境变量

在`.env`文件中配置：
```env
# OpenAI API配置
API_KEY=your_openai_api_key
BASE_URL=https://api.openai-proxy.org/v1

# RAG配置
RAG_EMBED_MODEL=text-embedding-3-small
RAG_LLM_MODEL=gpt-4o-mini
QDRANT_URL=http://localhost:6333
QDRANT_GRPC_PORT=6334
QDRANT_PREFER_GRPC=True
QDRANT_COLLECTION_NAME=course_materials
```

### 3. 启动服务

```bash
python -m app.main
```

服务将在 http://localhost:8000 启动

## API使用

### 建立文档索引

```bash
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -F "file=@your_document.md" \
  -F "course_id=course_001" \
  -F "course_material_id=material_001" \
  -F "course_material_name=Python基础教程"
```

### RAG问答查询

**检索模式**：
```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是Python函数？",
    "mode": "query",
    "course_id": "course_001"
  }'
```

**直接聊天模式**：
```bash
curl -X POST "http://localhost:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "你好，请介绍一下自己",
    "mode": "chat"
  }'
```

### 管理集合

**获取集合列表**：
```bash
curl "http://localhost:8000/api/v1/rag/collections"
```

**删除集合**：
```bash
curl -X DELETE "http://localhost:8000/api/v1/rag/collections/collection_name"
```

**健康检查**：
```bash
curl "http://localhost:8000/api/v1/rag/health"
```

## 工具脚本

### 批量索引构建

```bash
python scripts/build_rag_index.py /path/to/documents --course-id course_001
```

### 数据管理

```bash
# 列出所有集合
python scripts/rag_data_manager.py list

# 获取集合信息
python scripts/rag_data_manager.py info collection_name

# 备份集合信息
python scripts/rag_data_manager.py backup

# 创建新集合
python scripts/rag_data_manager.py create new_collection

# 删除集合
python scripts/rag_data_manager.py delete collection_name
```

## 测试

### 运行单元测试
```bash
python -m pytest tests/test_rag.py -v
```

### 运行演示测试
```bash
python test_rag_demo.py
```

## 配置说明

### RAG参数配置
- `RAG_CHUNK_SIZE=512`：文本分块大小
- `RAG_CHUNK_OVERLAP=50`：文本分块重叠
- `RAG_TOP_K=5`：检索返回的文档数量

### Qdrant配置
- `QDRANT_PREFER_GRPC=True`：优先使用gRPC连接（推荐）
- `QDRANT_GRPC_PORT=6334`：gRPC端口
- `QDRANT_COLLECTION_NAME=course_materials`：默认集合名称

## 故障排除

### 常见问题

1. **Qdrant连接失败**
   - 检查Qdrant服务是否运行：`curl http://localhost:6333/collections`
   - 检查端口是否被占用

2. **OpenAI API错误**
   - 验证API密钥是否正确
   - 检查网络连接和代理设置

3. **索引建立失败**
   - 检查文件格式（仅支持.md和.txt）
   - 验证文件内容编码（UTF-8）

4. **查询无结果**
   - 确认集合中有数据：`python scripts/rag_data_manager.py info collection_name`
   - 检查course_id过滤条件

### 日志查看

应用日志包含详细的错误信息，可以帮助诊断问题：
- RAG服务初始化日志
- 索引建立过程日志
- 查询处理日志
- Qdrant操作日志

## 性能优化建议

1. **使用gRPC连接**：比HTTP REST API性能更高
2. **批量索引**：使用脚本批量处理文档
3. **合理设置chunk_size**：根据文档类型调整分块大小
4. **缓存策略**：考虑对频繁查询的结果进行缓存

## 扩展功能

RAG模块设计为可扩展的架构，可以轻松添加：
- 更多文档格式支持（PDF、DOCX等）
- 不同的嵌入模型
- 混合搜索（dense + sparse vectors）
- 多语言支持
- 用户权限管理

## 支持

如有问题或建议，请查看：
- API文档：http://localhost:8000/docs
- 项目文档：`dev_docs/RAG_Module_Development_Plan.md`
- 测试用例：`tests/test_rag.py`
