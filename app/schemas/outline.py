"""
大纲生成相关的数据模型
定义请求和响应的数据结构
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败


class OutlineGenerateRequest(BaseModel):
    """大纲生成请求模型"""
    # 注意：文件上传通过 FastAPI 的 UploadFile 处理，不在这里定义

    # 必需参数
    course_id: str = Field(
        ...,
        description="课程ID，用于组织文件存储目录",
        min_length=1,
        max_length=50
    )

    course_material_id: str = Field(
        ...,
        description="课程材料ID，在同一course_id下必须唯一",
        min_length=1,
        max_length=50
    )

    material_name: str = Field(
        ...,
        description="材料名称，用于生成文件名",
        min_length=1,
        max_length=100
    )

    # 可选参数
    custom_prompt: Optional[str] = Field(
        None,
        description="自定义提示词，如果不提供则使用默认提示词",
        max_length=2000
    )

    include_refine: bool = Field(
        default=True,
        description="是否进行大纲精简处理"
    )

    llm_model: Optional[str] = Field(
        None,
        description="指定使用的模型名称，如果不提供则使用配置中的默认模型",
        alias="model_name"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "course_id": "0001",
                "course_material_id": "000001",
                "material_name": "python第八章",
                "custom_prompt": None,
                "include_refine": True,
                "model_name": "gpt-4o-mini"
            }
        }
        protected_namespaces = ()


class OutlineGenerateResponse(BaseModel):
    """大纲生成响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")

    # 课程信息
    course_id: Optional[str] = Field(None, description="课程ID")
    course_material_id: Optional[str] = Field(None, description="课程材料ID")
    material_name: Optional[str] = Field(None, description="材料名称")

    # 成功时返回的数据
    outline_content: Optional[str] = Field(None, description="生成的大纲内容")
    outline_file_path: Optional[str] = Field(None, description="大纲文件保存路径")
    original_file_path: Optional[str] = Field(None, description="原始文件保存路径")

    # 处理信息
    processing_time: Optional[float] = Field(None, description="处理时间(秒)")
    token_usage: Optional[Dict[str, int]] = Field(None, description="Token使用情况")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class OutlineTaskQuery(BaseModel):
    """大纲任务查询响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(..., description="状态消息")

    # 课程信息
    course_id: Optional[str] = Field(None, description="课程ID")
    course_material_id: Optional[str] = Field(None, description="课程材料ID")
    material_name: Optional[str] = Field(None, description="材料名称")

    # 任务详情
    original_filename: Optional[str] = Field(None, description="原始文件名")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")

    # 结果数据
    outline_content: Optional[str] = Field(None, description="生成的大纲内容")
    outline_file_path: Optional[str] = Field(None, description="大纲文件路径")

    # 处理信息
    processing_time: Optional[float] = Field(None, description="处理时间(秒)")
    error_message: Optional[str] = Field(None, description="错误信息")

    # 时间戳
    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class OutlineFileResponse(BaseModel):
    """获取outline文件响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")

    # 课程信息
    course_id: str = Field(..., description="课程ID")
    course_material_id: str = Field(..., description="课程材料ID")
    material_name: Optional[str] = Field(None, description="材料名称")

    # 文件信息
    file_path: str = Field(..., description="文件路径")
    file_content: str = Field(..., description="文件内容")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    last_modified: Optional[str] = Field(None, description="最后修改时间")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "文件获取成功",
                "course_id": "0001",
                "course_material_id": "000001",
                "material_name": "python第八章",
                "file_path": "data/outputs/outlines/0001/000001_python第八章.md",
                "file_content": "# 函数的核心概念与实践\n\n## 函数基础\n### 函数让重复任务只需写一次...",
                "file_size": 2048,
                "last_modified": "2024-08-14T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="详细错误信息")
    task_id: Optional[str] = Field(None, description="相关任务ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "文件验证失败",
                "detail": "不支持的文件类型: .pdf。支持的类型: .md, .txt",
                "task_id": None,
                "timestamp": "2024-08-14T10:30:00"
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    version: str = Field(default="0.1.0", description="应用版本")
    
    # 服务信息
    uptime: Optional[float] = Field(None, description="运行时间(秒)")
    
    # 依赖服务状态
    openai_api: Optional[str] = Field(None, description="OpenAI API状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-08-14T10:30:00",
                "version": "0.1.0",
                "uptime": 3600.5,
                "openai_api": "available"
            }
        }
