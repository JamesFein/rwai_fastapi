"""
文档索引服务
负责文档索引建立和管理、向量存储操作、集合管理
"""
import time
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

# LlamaIndex imports
from llama_index.core import Document, Settings
from qdrant_client.http.models import PointStruct

from app.core.config import Settings as AppSettings
from app.repositories.rag_repository import QdrantRepository
from app.services.rag.rag_settings import RAGConfigManager
from app.schemas.rag import (
    IndexRequest, IndexResponse, CollectionInfo
)


class DocumentIndexingService:
    """文档索引服务类"""
    
    def __init__(self, app_settings: AppSettings, rag_config_manager: RAGConfigManager):
        """
        初始化文档索引服务
        
        Args:
            app_settings: 应用配置
            rag_config_manager: RAG配置管理器
        """
        self.app_settings = app_settings
        self.rag_config_manager = rag_config_manager
        self.qdrant_repo = QdrantRepository(app_settings)
        
        # 确保RAG配置已初始化
        if not rag_config_manager.rag_settings:
            rag_config_manager.initialize(app_settings)
    
    async def build_index(self, request: IndexRequest) -> IndexResponse:
        """
        建立文档索引
        
        Args:
            request: 索引建立请求
            
        Returns:
            索引建立响应
        """
        start_time = time.time()
        
        try:
            # 使用指定的集合名称或默认名称
            collection_name = request.collection_name or self.app_settings.qdrant_collection_name
            
            logger.info(f"开始建立文档索引 - 集合: {collection_name}")
            
            # 确保集合存在
            self.qdrant_repo.create_collection(collection_name)
            
            # 创建文档对象
            document = Document(
                text=request.file_content,
                metadata={
                    "course_id": request.metadata.course_id,
                    "course_material_id": request.metadata.course_material_id,
                    "course_material_name": request.metadata.course_material_name,
                    "file_path": request.metadata.file_path,
                    "file_size": request.metadata.file_size,
                    "upload_time": request.metadata.upload_time or datetime.now().isoformat()
                }
            )
            
            # 文本分块
            text_splitter = self.rag_config_manager.get_text_splitter()
            nodes = text_splitter.get_nodes_from_documents([document])
            logger.info(f"文档分块完成，生成 {len(nodes)} 个文本块")
            
            # 生成向量并存储到Qdrant
            points = []
            for i, node in enumerate(nodes):
                # 生成嵌入向量
                embedding = Settings.embed_model.get_text_embedding(node.text)
                
                # 创建向量点
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": node.text,
                        "course_id": request.metadata.course_id,
                        "course_material_id": request.metadata.course_material_id,
                        "course_material_name": request.metadata.course_material_name,
                        "file_path": request.metadata.file_path,
                        "chunk_index": i,
                        "created_at": datetime.now().isoformat()
                    }
                )
                points.append(point)
            
            # 批量插入向量点
            success = self.qdrant_repo.upsert_points(collection_name, points)
            
            processing_time = time.time() - start_time
            
            if success:
                logger.info(f"文档索引建立成功 - 集合: {collection_name}, 耗时: {processing_time:.2f}s")
                return IndexResponse(
                    success=True,
                    message="索引建立成功",
                    document_count=1,
                    chunk_count=len(nodes),
                    processing_time=processing_time,
                    collection_name=collection_name
                )
            else:
                logger.error(f"文档索引建立失败 - 集合: {collection_name}")
                return IndexResponse(
                    success=False,
                    message="索引建立失败",
                    document_count=0,
                    chunk_count=0,
                    processing_time=processing_time,
                    collection_name=collection_name
                )
        
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"索引建立异常: {e}")
            return IndexResponse(
                success=False,
                message=f"索引建立失败: {str(e)}",
                document_count=0,
                chunk_count=0,
                processing_time=processing_time,
                collection_name=request.collection_name or self.app_settings.qdrant_collection_name
            )
    
    def get_collections(self) -> List[CollectionInfo]:
        """
        获取所有集合信息

        Returns:
            集合信息列表
        """
        try:
            logger.info("获取集合列表")
            collections = self.qdrant_repo.get_collections()
            logger.info(f"获取到 {len(collections)} 个集合")
            return collections
        except Exception as e:
            logger.error(f"获取集合列表失败: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """
        获取指定集合的详细信息

        Args:
            collection_name: 集合名称

        Returns:
            集合信息，如果不存在则返回None
        """
        try:
            logger.info(f"获取集合信息 - 集合: {collection_name}")
            collection_info = self.qdrant_repo.get_collection_info(collection_name)
            if collection_info:
                logger.info(f"集合信息获取成功 - 向量数量: {collection_info.vectors_count}")
            else:
                logger.warning(f"集合不存在: {collection_name}")
            return collection_info
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return None
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        删除指定集合

        Args:
            collection_name: 集合名称

        Returns:
            删除是否成功
        """
        try:
            logger.info(f"删除集合 - 集合: {collection_name}")
            success = self.qdrant_repo.delete_collection(collection_name)
            if success:
                logger.info(f"集合删除成功: {collection_name}")
            else:
                logger.error(f"集合删除失败: {collection_name}")
            return success
        except Exception as e:
            logger.error(f"删除集合异常: {e}")
            return False
    
    def count_documents(self, collection_name: str) -> int:
        """
        统计集合中的文档数量

        Args:
            collection_name: 集合名称

        Returns:
            文档数量
        """
        try:
            logger.info(f"统计文档数量 - 集合: {collection_name}")
            count = self.qdrant_repo.count_points(collection_name)
            logger.info(f"文档数量统计完成 - 集合: {collection_name}, 数量: {count}")
            return count
        except Exception as e:
            logger.error(f"统计文档数量失败: {e}")
            return 0
    
    def delete_documents_by_course(
        self,
        course_id: str,
        collection_name: Optional[str] = None
    ) -> int:
        """
        删除指定课程的所有文档

        Args:
            course_id: 课程ID
            collection_name: 集合名称，如果不指定则使用默认集合

        Returns:
            删除的文档数量
        """
        try:
            if collection_name is None:
                collection_name = self.app_settings.qdrant_collection_name

            logger.info(f"删除课程文档 - 课程ID: {course_id}, 集合: {collection_name}")

            # 构建过滤条件
            filter_condition = {
                "must": [
                    {"key": "course_id", "match": {"value": course_id}}
                ]
            }

            deleted_count = self.qdrant_repo.delete_vectors_by_filter(
                filter_condition, collection_name
            )

            logger.info(f"课程文档删除完成 - 课程ID: {course_id}, 删除数量: {deleted_count}")
            return deleted_count

        except Exception as e:
            logger.error(f"删除课程文档失败: {e}")
            return 0
    
    def delete_documents_by_material(
        self,
        course_id: str,
        course_material_id: str,
        collection_name: Optional[str] = None
    ) -> int:
        """
        删除指定课程材料的所有文档

        Args:
            course_id: 课程ID
            course_material_id: 课程材料ID
            collection_name: 集合名称，如果不指定则使用默认集合

        Returns:
            删除的文档数量
        """
        try:
            if collection_name is None:
                collection_name = self.app_settings.qdrant_collection_name

            logger.info(f"删除课程材料文档 - 课程ID: {course_id}, 材料ID: {course_material_id}, 集合: {collection_name}")

            # 构建过滤条件
            filter_condition = {
                "must": [
                    {"key": "course_id", "match": {"value": course_id}},
                    {"key": "course_material_id", "match": {"value": course_material_id}}
                ]
            }

            deleted_count = self.qdrant_repo.delete_vectors_by_filter(
                filter_condition, collection_name
            )

            logger.info(f"课程材料文档删除完成 - 材料ID: {course_material_id}, 删除数量: {deleted_count}")
            return deleted_count

        except Exception as e:
            logger.error(f"删除课程材料文档失败: {e}")
            return 0
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态信息
        
        Returns:
            服务状态字典
        """
        try:
            rag_settings_summary = self.rag_config_manager.get_settings_summary()
            
            return {
                "service_name": "DocumentIndexingService",
                "status": "healthy",
                "rag_config": rag_settings_summary,
                "qdrant_config": {
                    "url": self.app_settings.qdrant_url,
                    "grpc_port": self.app_settings.qdrant_grpc_port,
                    "prefer_grpc": self.app_settings.qdrant_prefer_grpc,
                    "default_collection": self.app_settings.qdrant_collection_name
                }
            }
        except Exception as e:
            return {
                "service_name": "DocumentIndexingService",
                "status": "error",
                "error": str(e)
            }
