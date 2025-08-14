# AI 功能后端 - 文本生成大纲模块

基于 FastAPI 构建的 AI 功能后端，专注于文档大纲生成功能，为后续 RAG 问答和 GraphRAG 模块预留扩展空间。

## 功能特性

### ✅ 已实现功能

- **文档大纲生成**: 上传 Markdown 或文本文件，生成结构化三层次大纲
- **课程化管理**: 基于 course_id 的文件组织和存储
- **材料唯一性**: 同一课程下 course_material_id 的唯一性验证
- **两阶段处理**: 原始大纲生成 + 标题精简优化
- **异步处理**: 基于 FastAPI 的高性能异步架构
- **文件安全**: 完整的文件上传验证和安全检查（仅支持 .md 和 .txt）
- **任务管理**: 任务状态跟踪和查询
- **性能监控**: 详细的性能指标和日志记录

### 🚧 预留功能

- **RAG 问答**: 基于 LlamaIndex 和 Qdrant 的问答系统
- **GraphRAG**: 知识图谱构建和导出

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

## API 使用示例

### 生成文档大纲

**新版本 API（推荐）**：

```bash
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@python第八章.md" \
  -F "course_id=0001" \
  -F "course_material_id=000001" \
  -F "material_name=python第八章" \
  -F "include_refine=true" \
  -F "model_name=gpt-4o-mini"
```

**参数说明**：

- `file`: 要处理的文件（仅支持 .md 和 .txt 格式）
- `course_id`: 课程 ID，用于文件组织
- `course_material_id`: 课程材料 ID，在同一课程下必须唯一
- `material_name`: 材料名称，用于生成文件名
- `include_refine`: 是否进行大纲精简（可选，默认 true）
- `model_name`: 指定模型名称（可选）
- `custom_prompt`: 自定义提示词（可选）

**文件存储规则**：

- 上传文件存储为：`data/uploads/{course_id}/{course_material_id}_{material_name}{extension}`
- 生成大纲存储为：`data/outputs/outlines/{course_id}/{course_material_id}_{material_name}.md`

**响应示例**：

```json
{
  "task_id": "12345678-1234-1234-1234-123456789012",
  "status": "completed",
  "message": "大纲生成成功",
  "course_id": "0001",
  "course_material_id": "000001",
  "material_name": "python第八章",
  "outline_content": "# 函数的核心概念与实践\n\n## 函数基础\n### 函数让重复任务只需写一次...",
  "outline_file_path": "data/outputs/outlines/0001/000001_python第八章.md",
  "original_file_path": "data/uploads/0001/000001_python第八章.md",
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

### 查询任务状态

```bash
curl -X GET "http://localhost:8000/api/v1/outline/task/{task_id}"
```

### 获取性能指标

```bash
curl -X GET "http://localhost:8000/api/v1/outline/metrics"
```

## 项目结构

```
ai-backend/
├── app/                    # 应用主目录
│   ├── api/               # API 路由
│   │   └── v1/           # API v1 版本
│   │       └── outline.py # 大纲生成 API
│   ├── core/             # 核心模块
│   │   ├── config.py     # 配置管理
│   │   ├── logging.py    # 日志配置
│   │   └── deps.py       # 依赖注入
│   ├── schemas/          # 数据模型
│   │   └── outline.py    # 大纲相关模型
│   ├── services/         # 业务逻辑
│   │   └── outline_service.py # 大纲生成服务
│   ├── utils/            # 工具函数
│   │   ├── fileio.py     # 文件操作
│   │   ├── idgen.py      # ID 生成
│   │   └── timers.py     # 时间工具
│   ├── constants/        # 常量定义
│   │   └── paths.py      # 路径常量
│   ├── prompts/          # 提示词模板
│   │   ├── outline_generation.md # 大纲生成提示词
│   │   └── outline_refine.md     # 大纲精简提示词
│   └── main.py           # 应用入口
├── data/                 # 数据目录
│   ├── uploads/          # 上传文件（按课程ID组织）
│   │   ├── 0001/         # 课程0001的文件
│   │   │   ├── 000001_python第八章.md
│   │   │   └── 000002_python第九章.txt
│   │   └── 0002/         # 课程0002的文件
│   ├── outputs/          # 输出文件
│   │   └── outlines/     # 大纲输出（按课程ID组织）
│   │       ├── 0001/     # 课程0001的大纲
│   │       │   ├── 000001_python第八章.md
│   │       │   └── 000002_python第九章.md
│   │       └── 0002/     # 课程0002的大纲
│   └── tmp/              # 临时文件
├── tests/                # 测试文件
├── requirements.txt      # 依赖列表
├── .env.example         # 环境变量模板
└── README.md            # 项目说明
```

## 配置说明

主要配置项（在 `.env` 文件中设置）：

```env
# OpenAI API 配置
API_KEY=your_openai_api_key
BASE_URL=https://api.openai.com/v1
OUTLINE_MODEL=gpt-4o-mini
REFINE_MODEL=gpt-4o-mini

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 文件配置
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.md,.txt
```

## 提示词说明

项目使用两阶段提示词处理：

1. **大纲生成阶段** (`app/prompts/outline_generation.md`)

   - 将文档转换为二级和三级标题的结构化大纲
   - 基于 `final_md2mindmap.ipynb` 的提示词设计

2. **大纲精简阶段** (`app/prompts/outline_refine.md`)
   - 添加合适的一级标题
   - 将二级标题精简为简洁短语
   - 保持三级标题不变

详细的提示词文档请参考 `prompts_documentation.md`。

## 文件管理系统

### 课程化文件组织

系统采用基于课程的文件组织方式，支持多课程、多材料的结构化管理：

#### 文件命名规则

1. **上传文件存储**：

   - 路径：`data/uploads/{course_id}/{course_material_id}_{material_name}{extension}`
   - 示例：`data/uploads/0001/000001_python第八章.md`

2. **大纲文件存储**：
   - 路径：`data/outputs/outlines/{course_id}/{course_material_id}_{material_name}.md`
   - 示例：`data/outputs/outlines/0001/000001_python第八章.md`

#### 唯一性约束

- 在同一个 `course_id` 下，`course_material_id` 必须唯一
- 系统会自动检查并阻止重复的 `course_material_id`
- 支持不同课程使用相同的 `course_material_id`

#### 支持的文件格式

- **Markdown 文件**：`.md`
- **文本文件**：`.txt`

#### 文件安全

- 自动清理文件名中的危险字符
- 路径遍历攻击防护
- 文件大小限制（默认 10MB）
- 文件类型验证

### 使用示例

```bash
# 上传第一个材料
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -F "file=@python基础.md" \
  -F "course_id=CS101" \
  -F "course_material_id=001" \
  -F "material_name=python基础"

# 上传同一课程的第二个材料
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -F "file=@python进阶.md" \
  -F "course_id=CS101" \
  -F "course_material_id=002" \
  -F "material_name=python进阶"

# 尝试上传重复的 course_material_id（会失败）
curl -X POST "http://localhost:8000/api/v1/outline/generate" \
  -F "file=@python补充.md" \
  -F "course_id=CS101" \
  -F "course_material_id=001" \
  -F "material_name=python补充"
# 错误响应：课程材料ID '001' 在课程 'CS101' 中已存在
```

## 开发指南

### 添加新功能

1. 在 `app/schemas/` 中定义数据模型
2. 在 `app/services/` 中实现业务逻辑
3. 在 `app/api/v1/` 中添加 API 路由
4. 在 `app/main.py` 中注册路由

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest tests/
```

### 代码格式化

```bash
# 安装格式化工具
pip install black isort

# 格式化代码
black app/
isort app/
```

## 部署说明

### Docker 部署

```bash
# 构建镜像
docker build -t ai-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env ai-backend
```

### 生产环境

建议使用 Gunicorn + Uvicorn 部署：

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 故障排除

### 常见问题

1. **OpenAI API 调用失败**

   - 检查 API 密钥是否正确
   - 确认网络连接正常
   - 查看日志中的详细错误信息

2. **文件上传失败**

   - 检查文件大小是否超过限制
   - 确认文件格式是否支持
   - 检查磁盘空间是否充足

3. **服务启动失败**
   - 检查端口是否被占用
   - 确认环境变量配置正确
   - 查看启动日志中的错误信息

### 日志查看

应用日志包含详细的调试信息，包括：

- 请求处理过程
- API 调用详情
- 性能指标
- 错误堆栈

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请创建 Issue 或联系开发团队。
