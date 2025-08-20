"""
统一课程材料处理服务
集成文件上传、大纲生成、RAG索引建立的完整流程
"""
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile, HTTPException

from ...core.logging import get_logger
from ...core.config import get_settings
from ...core.deps import save_upload_file
from ...constants.paths import UPLOADS_DIR
from ...schemas.course_materials import (
    CourseProcessRequest, CourseProcessResponse, ProcessingStatus, ProcessingStep
)
from ...schemas.rag import DocumentMetadata, IndexRequest
from ...services.outline.outline_service import outline_service
from ...services.rag.document_indexing_service import DocumentIndexingService
from ...services.rag.rag_settings import get_rag_config_manager
from ...services.course_material.cleanup_service import cleanup_service
from ...utils.idgen import IDGenerator, path_generator
from ...utils.validation import CourseValidation, FileValidation
from ...utils.fileio import file_utils

logger = get_logger("course_material_process_service")


class CourseMaterialProcessService:
    """统一课程材料处理服务"""
    
    def __init__(self):
        self.settings = get_settings()
        # 存储任务状态的简单内存存储（生产环境应使用数据库）
        self.task_storage: Dict[str, CourseProcessResponse] = {}

        # 初始化文档索引服务
        rag_config_manager = get_rag_config_manager()
        self.document_indexing_service = DocumentIndexingService(self.settings, rag_config_manager)
    
    async def process_course_material(
        self,
        file: UploadFile,
        request: CourseProcessRequest
    ) -> CourseProcessResponse:
        """
        处理课程材料的完整流程
        
        Args:
            file: 上传的文件
            request: 处理请求
            
        Returns:
            处理响应
        """
        task_id = IDGenerator.generate_task_id()
        start_time = time.time()
        
        # 初始化响应对象
        response = CourseProcessResponse(
            task_id=task_id,
            status=ProcessingStatus.UPLOADING,
            message="开始处理课程材料",
            current_step="uploading",
            course_id=request.course_id,
            course_material_id=request.course_material_id,
            material_name=request.material_name,
            original_filename=file.filename,
            file_size=0
        )
        
        # 存储任务状态
        self.task_storage[task_id] = response
        
        try:
            logger.info(f"开始处理课程材料 - 任务ID: {task_id}")
            
            # 第一阶段：文件上传验证
            await self._update_task_status(
                task_id, ProcessingStatus.UPLOADING, "文件上传验证中", "uploading"
            )
            
            upload_result = await self._process_file_upload(file, request, task_id)
            if not upload_result["success"]:
                await self._handle_processing_error(
                    task_id, "uploading", upload_result["error"]
                )
                return self.task_storage[task_id]
            
            # 更新文件信息
            response.upload_file_path = upload_result["file_path"]
            response.file_size = upload_result["file_size"]
            response.completed_steps = 1
            response.progress_percentage = 33.3
            
            # 第二阶段：大纲生成
            await self._update_task_status(
                task_id, ProcessingStatus.OUTLINE_GENERATING, "大纲生成中", "outline_generating"
            )
            
            outline_result = await self._process_outline_generation(
                upload_result["file_content"], request, task_id
            )
            if not outline_result["success"]:
                await self._handle_processing_error(
                    task_id, "outline_generating", outline_result["error"]
                )
                return self.task_storage[task_id]
            
            # 更新大纲信息
            response.outline_file_path = outline_result["outline_path"]
            response.outline_content = outline_result["outline_content"]
            response.token_usage = outline_result["token_usage"]
            response.completed_steps = 2
            response.progress_percentage = 66.6
            
            # 第三阶段：RAG索引建立
            if request.enable_rag_indexing:
                await self._update_task_status(
                    task_id, ProcessingStatus.RAG_INDEXING, "RAG索引建立中", "rag_indexing"
                )
                
                rag_result = await self._process_rag_indexing(
                    upload_result["file_content"], request, task_id
                )
                if not rag_result["success"]:
                    await self._handle_processing_error(
                        task_id, "rag_indexing", rag_result["error"]
                    )
                    return self.task_storage[task_id]
                
                # 更新RAG信息
                response.rag_index_status = "completed"
                response.rag_collection_name = rag_result["collection_name"]
                response.rag_document_count = rag_result["document_count"]
            else:
                response.rag_index_status = "skipped"
            
            # 第四阶段：完成确认
            response.completed_steps = 3
            response.progress_percentage = 100.0
            response.total_processing_time = time.time() - start_time
            response.completed_at = datetime.now()
            
            await self._update_task_status(
                task_id, ProcessingStatus.COMPLETED, "课程材料处理完成", "completed"
            )
            
            logger.info(f"课程材料处理完成 - 任务ID: {task_id}, 耗时: {response.total_processing_time:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"课程材料处理异常 - 任务ID: {task_id}, 错误: {str(e)}")
            await self._handle_processing_error(task_id, "unknown", str(e))
            return self.task_storage[task_id]
    
    async def _process_file_upload(
        self,
        file: UploadFile,
        request: CourseProcessRequest,
        task_id: str
    ) -> Dict[str, Any]:
        """处理文件上传"""
        try:
            # 文件验证
            allowed_extensions = ['.md', '.txt']
            if not FileValidation.validate_file_extension(file.filename, allowed_extensions):
                return {
                    "success": False,
                    "error": f"文件类型不支持: {Path(file.filename).suffix}，支持的类型: {', '.join(allowed_extensions)}"
                }

            if not FileValidation.validate_filename_characters(file.filename):
                return {
                    "success": False,
                    "error": "文件名包含不安全字符"
                }
            
            # 课程验证
            try:
                CourseValidation.validate_course_material_id_unique(
                    request.course_id, request.course_material_id
                )
            except HTTPException as e:
                return {
                    "success": False,
                    "error": e.detail
                }
            
            # 生成文件保存路径
            file_path = path_generator.generate_course_upload_path(
                base_dir=UPLOADS_DIR,
                course_id=request.course_id,
                course_material_id=request.course_material_id,
                material_name=request.material_name,
                file_extension=Path(file.filename).suffix
            )
            
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            file_size = await save_upload_file(file, file_path)
            
            # 读取文件内容
            file_content = await file_utils.read_text_file_safe(file_path)
            
            logger.info(f"文件上传成功 - 任务ID: {task_id}, 路径: {file_path}")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "file_size": file_size,
                "file_content": file_content
            }
            
        except Exception as e:
            logger.error(f"文件上传失败 - 任务ID: {task_id}, 错误: {str(e)}")
            return {
                "success": False,
                "error": f"文件上传失败: {str(e)}"
            }
    
    async def _process_outline_generation(
        self,
        file_content: str,
        request: CourseProcessRequest,
        task_id: str
    ) -> Dict[str, Any]:
        """处理大纲生成"""
        try:
            # 调用大纲生成服务
            outline_response = await outline_service.process_outline_generation(
                file_content=file_content,
                original_filename=f"{request.material_name}.md",
                custom_prompt=request.custom_prompt,
                include_refine=request.include_refine,
                model_name=request.llm_model,
                course_id=request.course_id,
                course_material_id=request.course_material_id,
                material_name=request.material_name,
                task_id=task_id  # 传入统一的task_id
            )
            
            if outline_response.status.value != "completed":
                return {
                    "success": False,
                    "error": f"大纲生成失败: {outline_response.message}"
                }
            
            logger.info(f"大纲生成成功 - 任务ID: {task_id}")
            
            return {
                "success": True,
                "outline_path": outline_response.outline_file_path,
                "outline_content": outline_response.outline_content,
                "token_usage": outline_response.token_usage
            }
            
        except Exception as e:
            logger.error(f"大纲生成失败 - 任务ID: {task_id}, 错误: {str(e)}")
            return {
                "success": False,
                "error": f"大纲生成失败: {str(e)}"
            }

    async def _process_rag_indexing(
        self,
        file_content: str,
        request: CourseProcessRequest,
        task_id: str
    ) -> Dict[str, Any]:
        """处理RAG索引建立"""
        try:
            # 构建文档元数据
            metadata = DocumentMetadata(
                course_id=request.course_id,
                course_material_id=request.course_material_id,
                course_material_name=request.material_name,
                file_path=None,  # 这里可以设置文件路径
                file_size=len(file_content.encode('utf-8')),
                upload_time=datetime.now().isoformat()
            )

            # 构建索引请求
            index_request = IndexRequest(
                file_content=file_content,
                metadata=metadata,
                collection_name=request.rag_collection_name
            )

            # 调用新的文档索引服务建立索引
            index_response = await self.document_indexing_service.build_index(index_request)

            if not index_response.success:
                return {
                    "success": False,
                    "error": f"RAG索引建立失败: {index_response.message}"
                }

            logger.info(f"RAG索引建立成功 - 任务ID: {task_id}")

            return {
                "success": True,
                "collection_name": index_response.collection_name,
                "document_count": index_response.chunk_count
            }

        except Exception as e:
            logger.error(f"RAG索引建立失败 - 任务ID: {task_id}, 错误: {str(e)}")
            return {
                "success": False,
                "error": f"RAG索引建立失败: {str(e)}"
            }

    async def _update_task_status(
        self,
        task_id: str,
        status: ProcessingStatus,
        message: str,
        current_step: str
    ):
        """更新任务状态"""
        if task_id in self.task_storage:
            response = self.task_storage[task_id]
            response.status = status
            response.message = message
            response.current_step = current_step

            # 添加处理步骤记录
            step = ProcessingStep(
                step_name=current_step,
                status=status,
                message=message,
                start_time=datetime.now()
            )
            response.processing_steps.append(step)

    async def _handle_processing_error(
        self,
        task_id: str,
        error_step: str,
        error_message: str
    ):
        """处理错误情况"""
        if task_id in self.task_storage:
            response = self.task_storage[task_id]
            response.status = ProcessingStatus.FAILED
            response.message = f"处理失败: {error_message}"
            response.error_step = error_step
            response.error_message = error_message

            # 添加错误步骤记录
            step = ProcessingStep(
                step_name=error_step,
                status=ProcessingStatus.FAILED,
                message=error_message,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=error_message
            )
            response.processing_steps.append(step)

            # 自动清理已完成的操作
            try:
                from ...schemas.course_materials import CleanupRequest
                cleanup_request = CleanupRequest(
                    course_id=response.course_id,
                    course_material_id=response.course_material_id,
                    cleanup_files=True,
                    cleanup_rag_data=True,
                    cleanup_task_data=False,  # 保留任务数据以便查看错误信息
                    force_cleanup=True
                )

                await cleanup_service.cleanup_course_material(cleanup_request)
                logger.info(f"自动清理完成 - 任务ID: {task_id}")

            except Exception as cleanup_error:
                logger.error(f"自动清理失败 - 任务ID: {task_id}, 错误: {str(cleanup_error)}")

    def get_task_status(self, task_id: str) -> Optional[CourseProcessResponse]:
        """获取任务状态"""
        return self.task_storage.get(task_id)

    def remove_task(self, task_id: str) -> bool:
        """移除任务记录"""
        if task_id in self.task_storage:
            del self.task_storage[task_id]
            return True
        return False


# 创建全局课程材料处理服务实例
course_material_process_service = CourseMaterialProcessService()
