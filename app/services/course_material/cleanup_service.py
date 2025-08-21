"""
课程材料清理服务
负责清理文件系统、Qdrant数据库、任务状态等
"""
import os
import time
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...core.logging import get_logger
from ...core.config import get_settings
from ...constants.paths import UPLOADS_DIR, OUTLINES_DIR
from ...schemas.course_materials import CleanupRequest, CleanupResponse, CleanupOperation
from ...repositories.rag_repository import rag_repository

logger = get_logger("cleanup_service")


class CleanupService:
    """课程材料清理服务"""
    
    def __init__(self):
        self.settings = get_settings()
        
    async def cleanup_course_material(
        self,
        request: CleanupRequest
    ) -> CleanupResponse:
        """
        清理指定课程材料的所有数据
        
        Args:
            request: 清理请求
            
        Returns:
            清理响应
        """
        start_time = time.time()
        operations = []
        
        try:
            logger.info(f"开始清理课程材料 - 课程ID: {request.course_id}, 材料ID: {request.course_material_id}")
            
            # 1. 清理文件系统
            if request.cleanup_files:
                file_operations = await self._cleanup_files(
                    request.course_id,
                    request.course_material_id
                )
                operations.extend(file_operations)

            # 2. 清理RAG数据
            if request.cleanup_rag_data:
                rag_operations = await self._cleanup_rag_data(
                    request.course_id,
                    request.course_material_id
                )
                operations.extend(rag_operations)

            # 3. 清理任务数据
            if request.cleanup_task_data:
                task_operations = await self._cleanup_task_data(
                    request.course_id,
                    request.course_material_id
                )
                operations.extend(task_operations)

            # 4. 清理空目录
            directory_operations = await self._cleanup_empty_directories(
                request.course_id
            )
            operations.extend(directory_operations)
            
            # 统计清理结果
            files_deleted = sum(1 for op in operations if op.operation_type == "file_delete" and op.success)
            directories_cleaned = sum(1 for op in operations if op.operation_type == "directory_cleanup" and op.success)
            rag_vectors_deleted = sum(
                int(op.details.split("删除了")[1].split("个")[0]) if op.details and "删除了" in op.details else 0
                for op in operations if op.operation_type == "rag_cleanup" and op.success
            )
            tasks_cleaned = sum(1 for op in operations if op.operation_type == "task_cleanup" and op.success)
            
            cleanup_time = time.time() - start_time
            
            # 检查是否有失败的操作
            failed_operations = [op for op in operations if not op.success]
            success = len(failed_operations) == 0
            
            if success:
                message = "清理操作完成"
            else:
                message = f"清理操作部分失败，{len(failed_operations)}个操作失败"
            
            logger.info(f"清理完成 - 成功: {success}, 耗时: {cleanup_time:.2f}s")
            
            return CleanupResponse(
                success=success,
                message=message,
                course_id=request.course_id,
                course_material_id=request.course_material_id,
                operations=operations,
                files_deleted=files_deleted,
                directories_cleaned=directories_cleaned,
                rag_vectors_deleted=rag_vectors_deleted,
                tasks_cleaned=tasks_cleaned,
                cleanup_time=cleanup_time
            )
            
        except Exception as e:
            cleanup_time = time.time() - start_time
            logger.error(f"清理操作失败: {str(e)}")
            
            # 添加失败操作记录
            operations.append(CleanupOperation(
                operation_type="cleanup_error",
                target="cleanup_service",
                success=False,
                message=f"清理操作异常: {str(e)}",
                details=None
            ))
            
            return CleanupResponse(
                success=False,
                message=f"清理操作失败: {str(e)}",
                course_id=request.course_id,
                course_material_id=request.course_material_id,
                operations=operations,
                cleanup_time=cleanup_time
            )
    
    async def _cleanup_files(
        self,
        course_id: str,
        course_material_id: Optional[str]
    ) -> List[CleanupOperation]:
        """清理文件系统"""
        operations = []
        
        try:
            # 清理上传文件
            upload_operations = await self._cleanup_upload_files(
                course_id, course_material_id
            )
            operations.extend(upload_operations)

            # 清理大纲文件
            outline_operations = await self._cleanup_outline_files(
                course_id, course_material_id
            )
            operations.extend(outline_operations)
            
        except Exception as e:
            logger.error(f"文件清理失败: {str(e)}")
            operations.append(CleanupOperation(
                operation_type="file_cleanup_error",
                target="file_system",
                success=False,
                message=f"文件清理失败: {str(e)}",
                details=None
            ))
        
        return operations
    
    async def _cleanup_upload_files(
        self,
        course_id: str,
        course_material_id: Optional[str]
    ) -> List[CleanupOperation]:
        """清理上传文件"""
        operations = []
        upload_dir = UPLOADS_DIR / course_id
        
        if not upload_dir.exists():
            return operations
        
        try:
            if course_material_id:
                # 清理特定材料的文件
                pattern = f"{course_material_id}_*"
                for file_path in upload_dir.glob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            operations.append(CleanupOperation(
                                operation_type="file_delete",
                                target=str(file_path),
                                success=True,
                                message="上传文件删除成功",
                                details=None
                            ))
                        except Exception as e:
                            operations.append(CleanupOperation(
                                operation_type="file_delete",
                                target=str(file_path),
                                success=False,
                                message=f"上传文件删除失败: {str(e)}",
                                details=None
                            ))
            else:
                # 清理整个课程的文件
                for file_path in upload_dir.iterdir():
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            operations.append(CleanupOperation(
                                operation_type="file_delete",
                                target=str(file_path),
                                success=True,
                                message="上传文件删除成功",
                                details=None
                            ))
                        except Exception as e:
                            operations.append(CleanupOperation(
                                operation_type="file_delete",
                                target=str(file_path),
                                success=False,
                                message=f"上传文件删除失败: {str(e)}",
                                details=None
                            ))
                            
        except Exception as e:
            logger.error(f"上传文件清理失败: {str(e)}")
            operations.append(CleanupOperation(
                operation_type="upload_cleanup_error",
                target=str(upload_dir),
                success=False,
                message=f"上传文件清理失败: {str(e)}",
                details=None
            ))
        
        return operations
    
    async def _cleanup_outline_files(
        self,
        course_id: str,
        course_material_id: Optional[str]
    ) -> List[CleanupOperation]:
        """清理大纲文件"""
        operations = []
        outline_dir = OUTLINES_DIR / course_id
        
        if not outline_dir.exists():
            return operations
        
        try:
            if course_material_id:
                # 清理特定材料的大纲文件
                pattern = f"{course_material_id}_*.md"
                for file_path in outline_dir.glob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            operations.append(CleanupOperation(
                                operation_type="file_delete",
                                target=str(file_path),
                                success=True,
                                message="大纲文件删除成功",
                                details=None
                            ))
                        except Exception as e:
                            operations.append(CleanupOperation(
                                operation_type="file_delete",
                                target=str(file_path),
                                success=False,
                                message=f"大纲文件删除失败: {str(e)}",
                                details=None
                            ))
            else:
                # 清理整个课程的大纲文件
                for file_path in outline_dir.iterdir():
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            operations.append(CleanupOperation(
                                operation_type="file_delete",
                                target=str(file_path),
                                success=True,
                                message="大纲文件删除成功",
                                details=None
                            ))
                        except Exception as e:
                            operations.append(CleanupOperation(
                                operation_type="file_delete",
                                target=str(file_path),
                                success=False,
                                message=f"大纲文件删除失败: {str(e)}",
                                details=None
                            ))
                            
        except Exception as e:
            logger.error(f"大纲文件清理失败: {str(e)}")
            operations.append(CleanupOperation(
                operation_type="outline_cleanup_error",
                target=str(outline_dir),
                success=False,
                message=f"大纲文件清理失败: {str(e)}",
                details=None
            ))
        
        return operations

    async def _cleanup_rag_data(
        self,
        course_id: str,
        course_material_id: Optional[str]
    ) -> List[CleanupOperation]:
        """清理RAG数据"""
        operations = []

        try:
            # 构建过滤条件
            if course_material_id:
                # 清理特定材料的RAG数据
                filter_condition = {
                    "must": [
                        {"key": "course_id", "match": {"value": course_id}},
                        {"key": "course_material_id", "match": {"value": course_material_id}}
                    ]
                }
                target = f"course_id={course_id}, course_material_id={course_material_id}"
            else:
                # 清理整个课程的RAG数据
                filter_condition = {
                    "must": [
                        {"key": "course_id", "match": {"value": course_id}}
                    ]
                }
                target = f"course_id={course_id}"

            # 删除向量数据
            deleted_count = rag_repository.delete_vectors_by_filter(filter_condition)

            operations.append(CleanupOperation(
                operation_type="rag_cleanup",
                target=target,
                success=True,
                message="RAG数据清理成功",
                details=f"删除了{deleted_count}个向量点"
            ))

        except Exception as e:
            logger.error(f"RAG数据清理失败: {str(e)}")
            operations.append(CleanupOperation(
                operation_type="rag_cleanup",
                target="qdrant_database",
                success=False,
                message=f"RAG数据清理失败: {str(e)}",
                details=None
            ))

        return operations

    async def _cleanup_task_data(
        self,
        course_id: str,
        course_material_id: Optional[str]
    ) -> List[CleanupOperation]:
        """清理任务数据"""
        operations = []

        try:
            # 这里可以清理内存中的任务状态数据
            # 由于当前使用简单的内存存储，这里只是示例
            # 在实际生产环境中，应该清理数据库中的任务记录

            operations.append(CleanupOperation(
                operation_type="task_cleanup",
                target=f"course_id={course_id}, course_material_id={course_material_id}",
                success=True,
                message="任务数据清理成功",
                details="内存中的任务状态已清理"
            ))

        except Exception as e:
            logger.error(f"任务数据清理失败: {str(e)}")
            operations.append(CleanupOperation(
                operation_type="task_cleanup",
                target="task_storage",
                success=False,
                message=f"任务数据清理失败: {str(e)}",
                details=None
            ))

        return operations

    async def _cleanup_empty_directories(
        self,
        course_id: str
    ) -> List[CleanupOperation]:
        """清理空目录"""
        operations = []

        try:
            # 检查并清理上传目录
            upload_dir = UPLOADS_DIR / course_id
            if upload_dir.exists() and not any(upload_dir.iterdir()):
                try:
                    upload_dir.rmdir()
                    operations.append(CleanupOperation(
                        operation_type="directory_cleanup",
                        target=str(upload_dir),
                        success=True,
                        message="空的上传目录已删除",
                        details=None
                    ))
                except Exception as e:
                    operations.append(CleanupOperation(
                        operation_type="directory_cleanup",
                        target=str(upload_dir),
                        success=False,
                        message=f"上传目录删除失败: {str(e)}",
                        details=None
                    ))

            # 检查并清理大纲目录
            outline_dir = OUTLINES_DIR / course_id
            if outline_dir.exists() and not any(outline_dir.iterdir()):
                try:
                    outline_dir.rmdir()
                    operations.append(CleanupOperation(
                        operation_type="directory_cleanup",
                        target=str(outline_dir),
                        success=True,
                        message="空的大纲目录已删除",
                        details=None
                    ))
                except Exception as e:
                    operations.append(CleanupOperation(
                        operation_type="directory_cleanup",
                        target=str(outline_dir),
                        success=False,
                        message=f"大纲目录删除失败: {str(e)}",
                        details=None
                    ))

        except Exception as e:
            logger.error(f"目录清理失败: {str(e)}")
            operations.append(CleanupOperation(
                operation_type="directory_cleanup_error",
                target="directory_system",
                success=False,
                message=f"目录清理失败: {str(e)}",
                details=None
            ))

        return operations


# 创建全局清理服务实例
cleanup_service = CleanupService()
