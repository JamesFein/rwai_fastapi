"""
大纲生成API路由模块
提供文档大纲生成的REST API接口
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path
import os
from datetime import datetime
import glob

from ...core.deps import (
    validate_upload_file,
    save_upload_file,
    read_text_file,
    get_current_settings
)
from ...core.config import Settings
from ...core.logging import get_logger
from ...schemas.outline import (
    OutlineGenerateResponse,
    OutlineTaskQuery,
    OutlineFileResponse,
    ErrorResponse,
    TaskStatus
)
from ...services.outline_service import outline_service
from ...utils.fileio import file_utils
from ...utils.idgen import IDGenerator, filename_generator, path_generator
from ...utils.timers import async_timer, performance_monitor
from ...utils.validation import CourseValidation, FileValidation
from ...constants.paths import UPLOADS_DIR, OUTLINES_DIR

logger = get_logger("outline_api")

router = APIRouter(prefix="/outline", tags=["大纲生成"])

# 存储任务状态的简单内存存储（生产环境应使用数据库）
task_storage = {}


@router.post(
    "/generate",
    response_model=OutlineGenerateResponse,
    summary="生成文档大纲",
    description="上传Markdown或文本文档并生成结构化大纲"
)
async def generate_outline(
    file: UploadFile = File(..., description="要处理的Markdown或文本文件(.md/.txt)"),
    course_id: str = Form(..., description="课程ID"),
    course_material_id: str = Form(..., description="课程材料ID"),
    material_name: str = Form(..., description="材料名称"),
    custom_prompt: Optional[str] = Form(None, description="自定义提示词"),
    include_refine: bool = Form(True, description="是否进行大纲精简"),
    model_name: Optional[str] = Form(None, description="指定模型名称"),
    settings: Settings = Depends(get_current_settings)
):
    """生成文档大纲"""
    
    task_id = IDGenerator.generate_task_id()
    
    try:
        async with async_timer(f"outline_generation_{task_id}") as timer:
            logger.info(f"开始处理大纲生成请求 - 任务ID: {task_id}, 课程: {course_id}, 材料: {course_material_id}, 文件: {file.filename}")

            # 验证输入参数
            if not course_id.strip():
                raise HTTPException(status_code=400, detail="课程ID不能为空")
            if not course_material_id.strip():
                raise HTTPException(status_code=400, detail="课程材料ID不能为空")
            if not material_name.strip():
                raise HTTPException(status_code=400, detail="材料名称不能为空")

            # 验证上传文件
            validated_file = await validate_upload_file(file, settings)

            # 验证文件扩展名（只允许.md和.txt）
            if not FileValidation.validate_file_extension(validated_file.filename, [".md", ".txt"]):
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件类型。只允许上传 .md 和 .txt 文件"
                )

            # 验证course_material_id的唯一性
            CourseValidation.validate_course_material_id_unique(
                course_id=course_id,
                course_material_id=course_material_id,
                uploads_base_dir=UPLOADS_DIR
            )

            # 获取文件扩展名
            file_extension = Path(validated_file.filename).suffix

            # 生成基于课程的上传路径
            upload_path = path_generator.generate_course_upload_path(
                base_dir=UPLOADS_DIR,
                course_id=course_id,
                course_material_id=course_material_id,
                material_name=material_name,
                file_extension=file_extension
            )

            # 确保目录存在
            upload_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存上传文件
            file_size = await save_upload_file(validated_file, upload_path)
            
            # 读取文件内容
            file_content = await file_utils.read_text_file_safe(upload_path)
            
            # 更新任务状态
            task_storage[task_id] = {
                "status": TaskStatus.PROCESSING,
                "original_filename": validated_file.filename,
                "upload_path": str(upload_path),
                "file_size": file_size,
                "created_at": timer.start_time
            }
            
            logger.info(f"文件处理完成，开始生成大纲 - 任务ID: {task_id}")
            
            # 调用大纲生成服务，传入API层的task_id
            result = await outline_service.process_outline_generation(
                file_content=file_content,
                original_filename=validated_file.filename,
                custom_prompt=custom_prompt,
                include_refine=include_refine,
                model_name=model_name,
                course_id=course_id,
                course_material_id=course_material_id,
                material_name=material_name,
                task_id=task_id  # 传入API层的task_id
            )

            # 更新任务存储
            task_storage[task_id].update({
                "status": result.status,
                "result": result,
                "completed_at": timer.get_elapsed()
            })

            # 记录性能指标
            performance_monitor.record_timing(
                "outline_generation",
                await timer.get_elapsed(),
                task_id=task_id,
                file_size=file_size,
                filename=validated_file.filename,
                include_refine=include_refine,
                model_name=model_name or settings.outline_model
            )

            logger.info(f"大纲生成完成 - 任务ID: {task_id}, 状态: {result.status}")

            # 设置原始文件路径
            result.original_file_path = str(upload_path)

            # 确保返回的结果使用正确的task_id
            result.task_id = task_id

            return result
            
    except HTTPException:
        # 更新任务状态为失败
        if task_id in task_storage:
            task_storage[task_id]["status"] = TaskStatus.FAILED
        raise
    except Exception as e:
        logger.error(f"大纲生成过程中发生错误 - 任务ID: {task_id}, 错误: {str(e)}")
        
        # 更新任务状态为失败
        if task_id in task_storage:
            task_storage[task_id]["status"] = TaskStatus.FAILED
            task_storage[task_id]["error"] = str(e)
        
        raise HTTPException(
            status_code=500,
            detail=f"大纲生成失败: {str(e)}"
        )


@router.get(
    "/task/{task_id}",
    response_model=OutlineTaskQuery,
    summary="查询任务状态",
    description="根据任务ID查询大纲生成任务的状态和结果"
)
async def get_task_status(task_id: str):
    """查询任务状态"""
    
    logger.info(f"查询任务状态 - 任务ID: {task_id}")
    
    if task_id not in task_storage:
        raise HTTPException(
            status_code=404,
            detail=f"任务不存在: {task_id}"
        )
    
    task_data = task_storage[task_id]
    
    # 构建响应
    response = OutlineTaskQuery(
        task_id=task_id,
        status=task_data["status"],
        message=f"任务状态: {task_data['status'].value}",
        original_filename=task_data.get("original_filename"),
        file_size=task_data.get("file_size"),
        created_at=task_data.get("created_at", 0)
    )
    
    # 如果任务完成，添加结果数据
    if task_data["status"] == TaskStatus.COMPLETED and "result" in task_data:
        result = task_data["result"]
        response.outline_content = result.outline_content
        response.outline_file_path = result.outline_file_path
        response.processing_time = result.processing_time
        response.completed_at = result.completed_at
    
    # 如果任务失败，添加错误信息
    elif task_data["status"] == TaskStatus.FAILED and "error" in task_data:
        response.error_message = task_data["error"]
    
    return response


@router.get(
    "/tasks",
    summary="获取任务列表",
    description="获取所有任务的状态列表"
)
async def list_tasks():
    """获取任务列表"""

    logger.info("获取任务列表")

    tasks = []
    for task_id, task_data in task_storage.items():
        # 处理时间戳，确保可以 JSON 序列化
        created_at = task_data.get("created_at")
        completed_at = task_data.get("completed_at")

        if isinstance(created_at, float):
            from datetime import datetime
            created_at = datetime.fromtimestamp(created_at).isoformat()
        elif hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()

        if isinstance(completed_at, float):
            from datetime import datetime
            completed_at = datetime.fromtimestamp(completed_at).isoformat()
        elif hasattr(completed_at, 'isoformat'):
            completed_at = completed_at.isoformat()

        task_info = {
            "task_id": task_id,
            "status": task_data["status"].value,
            "original_filename": task_data.get("original_filename"),
            "created_at": created_at,
            "completed_at": completed_at
        }
        tasks.append(task_info)

    return {
        "total": len(tasks),
        "tasks": tasks
    }


@router.delete(
    "/task/{task_id}",
    summary="删除任务",
    description="删除指定的任务记录"
)
async def delete_task(task_id: str):
    """删除任务"""
    
    logger.info(f"删除任务 - 任务ID: {task_id}")
    
    if task_id not in task_storage:
        raise HTTPException(
            status_code=404,
            detail=f"任务不存在: {task_id}"
        )
    
    # 删除任务记录
    del task_storage[task_id]
    
    return {
        "message": f"任务已删除: {task_id}"
    }


@router.get(
    "/metrics",
    summary="获取性能指标",
    description="获取大纲生成的性能统计信息"
)
async def get_metrics():
    """获取性能指标"""
    
    logger.info("获取性能指标")
    
    metrics = performance_monitor.get_metrics()
    
    return {
        "performance_metrics": metrics,
        "active_tasks": len([
            task for task in task_storage.values()
            if task["status"] == TaskStatus.PROCESSING
        ]),
        "total_tasks": len(task_storage)
    }


@router.get(
    "/file/{course_id}/{course_material_id}",
    response_model=OutlineFileResponse,
    summary="获取outline文件",
    description="根据课程ID和课程材料ID获取对应的outline文件内容"
)
async def get_outline_file(
    course_id: str,
    course_material_id: str
):
    """获取outline文件"""

    logger.info(f"获取outline文件 - 课程ID: {course_id}, 材料ID: {course_material_id}")

    try:
        # 验证参数
        if not course_id.strip():
            raise HTTPException(status_code=400, detail="课程ID不能为空")
        if not course_material_id.strip():
            raise HTTPException(status_code=400, detail="课程材料ID不能为空")

        # 构建目录路径
        course_dir = OUTLINES_DIR / course_id

        # 检查课程目录是否存在
        if not course_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"课程目录不存在: {course_id}"
            )

        # 查找匹配的文件（格式：{course_material_id}_{material_name}.md）
        pattern = f"{course_material_id}_*.md"
        matching_files = list(course_dir.glob(pattern))

        if not matching_files:
            raise HTTPException(
                status_code=404,
                detail=f"未找到课程材料文件: course_id={course_id}, course_material_id={course_material_id}"
            )

        if len(matching_files) > 1:
            logger.warning(f"找到多个匹配文件: {[f.name for f in matching_files]}")

        # 使用第一个匹配的文件
        outline_file = matching_files[0]

        # 读取文件内容
        try:
            file_content = await read_text_file(outline_file)
        except Exception as e:
            logger.error(f"读取文件失败: {outline_file}, 错误: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"读取文件失败: {str(e)}"
            )

        # 获取文件信息
        file_stat = outline_file.stat()
        file_size = file_stat.st_size
        last_modified = datetime.fromtimestamp(file_stat.st_mtime).isoformat()

        # 从文件名中提取材料名称
        filename_without_ext = outline_file.stem  # 去掉.md扩展名
        # 格式：{course_material_id}_{material_name}
        if filename_without_ext.startswith(f"{course_material_id}_"):
            material_name = filename_without_ext[len(f"{course_material_id}_"):]
        else:
            material_name = None

        logger.info(f"成功获取outline文件 - 路径: {outline_file}, 大小: {file_size}字节")

        return OutlineFileResponse(
            success=True,
            message="文件获取成功",
            course_id=course_id,
            course_material_id=course_material_id,
            material_name=material_name,
            file_path=str(outline_file),
            file_content=file_content,
            file_size=file_size,
            last_modified=last_modified
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取outline文件时发生错误 - 课程ID: {course_id}, 材料ID: {course_material_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取文件失败: {str(e)}"
        )
