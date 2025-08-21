"""
统一课程材料处理API路由
实现文件上传、大纲生成、RAG索引建立的一站式服务
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional

from ...core.logging import get_logger
from ...schemas.course_materials import (
    CourseProcessRequest, CourseProcessResponse, TaskStatusQuery,
    CleanupRequest, CleanupResponse, ProcessingStatus
)
from ...schemas.outline import ErrorResponse
from ...services.course_material.course_material_process_service import course_material_process_service
from ...services.course_material.cleanup_service import cleanup_service

logger = get_logger("course_materials_api")

router = APIRouter(prefix="/course-materials", tags=["课程材料处理"])


@router.post(
    "/process",
    response_model=CourseProcessResponse,
    summary="统一处理课程材料",
    description="上传课程材料并自动完成大纲生成和RAG索引建立"
)
async def process_course_material(
    file: UploadFile = File(..., description="课程材料文件（支持.md和.txt格式）"),
    course_id: str = Form(..., description="课程ID"),
    course_material_id: str = Form(..., description="课程材料ID"),
    material_name: str = Form(..., description="材料名称"),
    custom_prompt: Optional[str] = Form(None, description="自定义提示词"),
    include_refine: bool = Form(True, description="是否进行大纲精简处理"),
    model_name: Optional[str] = Form(None, description="指定使用的模型名称"),
    enable_rag_indexing: bool = Form(True, description="是否建立RAG索引"),
    rag_collection_name: Optional[str] = Form(None, description="RAG集合名称")
):
    """
    统一处理课程材料
    
    该API将按顺序执行以下步骤：
    1. 文件上传验证
    2. 大纲生成
    3. RAG索引建立（可选）
    
    处理过程中会提供实时进度反馈，失败时自动清理已完成的操作。
    """
    try:
        # 构建处理请求
        request = CourseProcessRequest(
            course_id=course_id,
            course_material_id=course_material_id,
            material_name=material_name,
            custom_prompt=custom_prompt,
            include_refine=include_refine,
            llm_model=model_name,
            enable_rag_indexing=enable_rag_indexing,
            rag_collection_name=rag_collection_name
        )
        
        # 执行处理
        response = await course_material_process_service.process_course_material(file, request)
        
        return response
        
    except Exception as e:
        logger.error(f"课程材料处理API异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"课程材料处理失败: {str(e)}"
        )


@router.get(
    "/tasks/{task_id}/status",
    response_model=TaskStatusQuery,
    summary="查询任务状态",
    description="查询课程材料处理任务的实时状态和进度"
)
async def get_task_status(task_id: str):
    """
    查询任务状态
    
    返回指定任务的当前状态、进度信息和处理结果。
    """
    try:
        # 获取任务状态
        task_response = course_material_process_service.get_task_status(task_id)
        
        if not task_response:
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 不存在"
            )
        
        # 转换为查询响应格式
        status_query = TaskStatusQuery(
            task_id=task_response.task_id,
            status=task_response.status,
            message=task_response.message,
            current_step=task_response.current_step,
            completed_steps=task_response.completed_steps,
            total_steps=task_response.total_steps,
            progress_percentage=task_response.progress_percentage,
            course_id=task_response.course_id,
            course_material_id=task_response.course_material_id,
            material_name=task_response.material_name,
            upload_file_path=task_response.upload_file_path,
            outline_file_path=task_response.outline_file_path,
            rag_index_status=task_response.rag_index_status,
            error_step=task_response.error_step,
            error_message=task_response.error_message,
            created_at=task_response.created_at
        )
        
        return status_query
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询任务状态异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"查询任务状态失败: {str(e)}"
        )


@router.delete(
    "/{course_id}/{course_material_id}",
    response_model=CleanupResponse,
    summary="清理指定课程材料",
    description="删除指定课程材料的所有数据，包括文件、大纲、RAG索引等"
)
async def cleanup_course_material(
    course_id: str,
    course_material_id: str,
    cleanup_files: bool = True,
    cleanup_rag_data: bool = True,
    cleanup_task_data: bool = True
):
    """
    清理指定课程材料
    
    删除指定课程材料的所有痕迹，包括：
    - 上传文件
    - 大纲文件
    - RAG向量数据
    - 任务状态记录
    """
    try:
        # 构建清理请求
        cleanup_request = CleanupRequest(
            course_id=course_id,
            course_material_id=course_material_id,
            cleanup_files=cleanup_files,
            cleanup_rag_data=cleanup_rag_data,
            cleanup_task_data=cleanup_task_data
        )
        
        # 执行清理
        cleanup_response = await cleanup_service.cleanup_course_material(cleanup_request)
        
        return cleanup_response
        
    except Exception as e:
        logger.error(f"清理课程材料异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"清理课程材料失败: {str(e)}"
        )





@router.get(
    "/health",
    summary="健康检查",
    description="检查课程材料处理服务的健康状态"
)
async def health_check():
    """
    健康检查
    
    检查各个组件的状态。
    """
    try:
        # 这里可以添加各种健康检查
        # 例如检查Qdrant连接、文件系统状态等
        
        return {
            "status": "healthy",
            "message": "课程材料处理服务运行正常",
            "components": {
                "outline_service": "available",
                "rag_service": "available",
                "cleanup_service": "available",
                "file_system": "available"
            }
        }
        
    except Exception as e:
        logger.error(f"健康检查异常: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": f"服务异常: {str(e)}"
            }
        )
