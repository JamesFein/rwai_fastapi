"""
课程管理API路由
专门处理课程级别的操作
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import shutil
from pathlib import Path
from urllib.parse import unquote

from ...core.logging import get_logger
from ...constants.paths import UPLOADS_DIR, OUTLINES_DIR
from ...repositories.rag_repository import rag_repository

logger = get_logger("course_api")
router = APIRouter(prefix="/course", tags=["课程管理"])


@router.delete("/{course_id}")
async def delete_course(course_id: str):
    """
    删除整个课程及其所有数据

    删除内容包括：
    - data/uploads/{course_id} 文件夹
    - data/outputs/outlines/{course_id} 文件夹
    - Qdrant中所有course_id匹配的向量点

    Args:
        course_id: 课程ID

    Returns:
        删除操作的结果信息
    """
    try:
        # URL解码course_id，处理中文字符
        course_id = unquote(course_id).strip()
        logger.info(f"开始删除课程: {course_id}")

        operations = []
        
        # 1. 删除上传文件夹
        upload_dir = UPLOADS_DIR / course_id
        upload_success = False
        upload_path = str(upload_dir)
        
        if upload_dir.exists():
            try:
                shutil.rmtree(upload_dir)
                upload_success = True
                logger.info(f"成功删除上传文件夹: {upload_path}")
            except Exception as e:
                logger.error(f"删除上传文件夹失败: {upload_path}, 错误: {str(e)}")
                upload_success = False
        else:
            upload_success = True  # 文件夹不存在也算成功
            logger.info(f"上传文件夹不存在: {upload_path}")
        
        operations.append({
            "type": "upload_folder",
            "success": upload_success,
            "path": upload_path
        })
        
        # 2. 删除大纲文件夹
        outline_dir = OUTLINES_DIR / course_id
        outline_success = False
        outline_path = str(outline_dir)
        
        if outline_dir.exists():
            try:
                shutil.rmtree(outline_dir)
                outline_success = True
                logger.info(f"成功删除大纲文件夹: {outline_path}")
            except Exception as e:
                logger.error(f"删除大纲文件夹失败: {outline_path}, 错误: {str(e)}")
                outline_success = False
        else:
            outline_success = True  # 文件夹不存在也算成功
            logger.info(f"大纲文件夹不存在: {outline_path}")
        
        operations.append({
            "type": "outline_folder", 
            "success": outline_success,
            "path": outline_path
        })
        
        # 3. 删除Qdrant向量数据
        qdrant_success = False
        deleted_count = 0

        try:
            filter_condition = {
                "must": [{"key": "course_id", "match": {"value": course_id}}]
            }
            # 注意：delete_vectors_by_filter 不是异步方法，不需要 await
            deleted_count = rag_repository.delete_vectors_by_filter(filter_condition)
            qdrant_success = True
            logger.info(f"成功删除Qdrant向量数据: {deleted_count}个向量点")
        except Exception as e:
            logger.error(f"删除Qdrant向量数据失败: {str(e)}")
            qdrant_success = False
        
        operations.append({
            "type": "qdrant_vectors",
            "success": qdrant_success,
            "deleted_count": deleted_count
        })
        
        # 检查是否所有操作都成功
        all_success = all(op["success"] for op in operations)
        
        if all_success:
            logger.info(f"课程 {course_id} 删除成功")
            return {
                "success": True,
                "message": f"课程 {course_id} 删除成功",
                "course_id": course_id,
                "operations": operations
            }
        else:
            logger.warning(f"课程 {course_id} 删除部分失败")
            return {
                "success": False,
                "message": f"课程 {course_id} 删除部分失败，请检查操作详情",
                "course_id": course_id,
                "operations": operations
            }
            
    except Exception as e:
        logger.error(f"删除课程异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"删除课程失败: {str(e)}"
        )
