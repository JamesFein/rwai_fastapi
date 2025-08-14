"""
统一课程材料处理相关的数据模型
定义请求和响应的数据结构
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    UPLOADING = "uploading"                    # 文件上传中
    OUTLINE_GENERATING = "outline_generating"  # 大纲生成中
    RAG_INDEXING = "rag_indexing"             # RAG索引建立中
    COMPLETED = "completed"                    # 处理完成
    FAILED = "failed"                         # 处理失败


class ProcessingStep(BaseModel):
    """处理步骤模型"""
    step_name: str = Field(..., description="步骤名称")
    status: ProcessingStatus = Field(..., description="步骤状态")
    message: str = Field(..., description="步骤消息")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    error_message: Optional[str] = Field(None, description="错误信息")


class CourseProcessRequest(BaseModel):
    """课程材料处理请求模型"""
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

    # RAG相关参数
    enable_rag_indexing: bool = Field(
        default=True,
        description="是否建立RAG索引"
    )

    rag_collection_name: Optional[str] = Field(
        None,
        description="RAG集合名称，如果不提供则使用默认集合"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "course_id": "0001",
                "course_material_id": "000001",
                "material_name": "python第八章",
                "custom_prompt": None,
                "include_refine": True,
                "model_name": "gpt-4o-mini",
                "enable_rag_indexing": True,
                "rag_collection_name": None
            }
        }
        protected_namespaces = ()


class CourseProcessResponse(BaseModel):
    """课程材料处理响应模型"""
    # 任务标识信息
    task_id: str = Field(..., description="任务ID")
    status: ProcessingStatus = Field(..., description="当前处理状态")
    message: str = Field(..., description="响应消息")

    # 进度信息
    current_step: str = Field(..., description="当前处理步骤")
    completed_steps: int = Field(default=0, description="已完成步骤数")
    total_steps: int = Field(default=3, description="总步骤数")
    progress_percentage: float = Field(default=0.0, description="进度百分比")

    # 文件信息
    course_id: str = Field(..., description="课程ID")
    course_material_id: str = Field(..., description="课程材料ID")
    material_name: str = Field(..., description="材料名称")
    original_filename: Optional[str] = Field(None, description="原始文件名")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")

    # 处理结果
    upload_file_path: Optional[str] = Field(None, description="上传文件保存路径")
    outline_file_path: Optional[str] = Field(None, description="大纲文件保存路径")
    outline_content: Optional[str] = Field(None, description="生成的大纲内容")
    rag_index_status: Optional[str] = Field(None, description="RAG索引状态")
    rag_collection_name: Optional[str] = Field(None, description="RAG集合名称")
    rag_document_count: Optional[int] = Field(None, description="RAG文档数量")

    # 错误信息
    error_step: Optional[str] = Field(None, description="出错的步骤")
    error_message: Optional[str] = Field(None, description="错误消息")

    # 处理信息
    processing_steps: List[ProcessingStep] = Field(default_factory=list, description="处理步骤详情")
    total_processing_time: Optional[float] = Field(None, description="总处理时间(秒)")
    token_usage: Optional[Dict[str, int]] = Field(None, description="Token使用情况")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "12345678-1234-1234-1234-123456789012",
                "status": "completed",
                "message": "课程材料处理完成",
                "current_step": "completed",
                "completed_steps": 3,
                "total_steps": 3,
                "progress_percentage": 100.0,
                "course_id": "0001",
                "course_material_id": "000001",
                "material_name": "python第八章",
                "original_filename": "python第八章.md",
                "file_size": 15360,
                "upload_file_path": "data/uploads/0001/000001_python第八章.md",
                "outline_file_path": "data/outputs/outlines/0001/000001_python第八章.md",
                "outline_content": "# 函数的核心概念与实践\n\n## 函数基础\n### 函数让重复任务只需写一次...",
                "rag_index_status": "completed",
                "rag_collection_name": "course_materials",
                "rag_document_count": 15,
                "error_step": None,
                "error_message": None,
                "total_processing_time": 45.5,
                "token_usage": {
                    "prompt_tokens": 1500,
                    "completion_tokens": 800,
                    "total_tokens": 2300
                },
                "created_at": "2024-08-14T10:30:00",
                "completed_at": "2024-08-14T10:30:45"
            }
        }


class TaskStatusQuery(BaseModel):
    """任务状态查询响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: ProcessingStatus = Field(..., description="当前处理状态")
    message: str = Field(..., description="状态消息")

    # 进度信息
    current_step: str = Field(..., description="当前处理步骤")
    completed_steps: int = Field(..., description="已完成步骤数")
    total_steps: int = Field(..., description="总步骤数")
    progress_percentage: float = Field(..., description="进度百分比")

    # 文件信息
    course_id: str = Field(..., description="课程ID")
    course_material_id: str = Field(..., description="课程材料ID")
    material_name: str = Field(..., description="材料名称")

    # 处理结果（如果已完成）
    upload_file_path: Optional[str] = Field(None, description="上传文件保存路径")
    outline_file_path: Optional[str] = Field(None, description="大纲文件保存路径")
    rag_index_status: Optional[str] = Field(None, description="RAG索引状态")

    # 错误信息
    error_step: Optional[str] = Field(None, description="出错的步骤")
    error_message: Optional[str] = Field(None, description="错误消息")

    # 时间信息
    created_at: datetime = Field(..., description="创建时间")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")


class CleanupOperation(BaseModel):
    """清理操作模型"""
    operation_type: str = Field(..., description="操作类型")
    target: str = Field(..., description="清理目标")
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="操作消息")
    details: Optional[str] = Field(None, description="详细信息")


class CleanupRequest(BaseModel):
    """清理请求模型"""
    course_id: str = Field(..., description="课程ID")
    course_material_id: Optional[str] = Field(None, description="课程材料ID，如果不提供则清理整个课程")
    cleanup_files: bool = Field(default=True, description="是否清理文件系统")
    cleanup_rag_data: bool = Field(default=True, description="是否清理RAG数据")
    cleanup_task_data: bool = Field(default=True, description="是否清理任务数据")
    force_cleanup: bool = Field(default=False, description="是否强制清理（忽略错误）")


class CleanupResponse(BaseModel):
    """清理响应模型"""
    success: bool = Field(..., description="清理是否成功")
    message: str = Field(..., description="清理消息")
    
    # 清理范围
    course_id: str = Field(..., description="课程ID")
    course_material_id: Optional[str] = Field(None, description="课程材料ID")
    
    # 清理操作列表
    operations: List[CleanupOperation] = Field(default_factory=list, description="清理操作列表")
    
    # 清理统计
    files_deleted: int = Field(default=0, description="删除的文件数量")
    directories_cleaned: int = Field(default=0, description="清理的目录数量")
    rag_vectors_deleted: int = Field(default=0, description="删除的RAG向量数量")
    tasks_cleaned: int = Field(default=0, description="清理的任务数量")
    
    # 时间信息
    cleanup_time: float = Field(..., description="清理耗时(秒)")
    timestamp: datetime = Field(default_factory=datetime.now, description="清理时间")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "清理操作完成",
                "course_id": "0001",
                "course_material_id": "000001",
                "operations": [
                    {
                        "operation_type": "file_cleanup",
                        "target": "data/uploads/0001/000001_python第八章.md",
                        "success": True,
                        "message": "文件删除成功",
                        "details": None
                    },
                    {
                        "operation_type": "rag_cleanup",
                        "target": "course_materials collection",
                        "success": True,
                        "message": "RAG数据清理成功",
                        "details": "删除了15个向量点"
                    }
                ],
                "files_deleted": 2,
                "directories_cleaned": 0,
                "rag_vectors_deleted": 15,
                "tasks_cleaned": 1,
                "cleanup_time": 2.5,
                "timestamp": "2024-08-14T10:35:00"
            }
        }
