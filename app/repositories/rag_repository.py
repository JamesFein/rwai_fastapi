"""
RAG存储仓库 - 负责Qdrant向量数据库操作
"""
from typing import List, Optional, Dict, Any
import asyncio
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from app.core.config import Settings
from app.schemas.rag import CollectionInfo


class QdrantRepository:
    """Qdrant向量数据库仓库类"""
    
    def __init__(self, settings: Settings):
        """初始化Qdrant客户端"""
        self.settings = settings
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Qdrant客户端"""
        try:
            if self.settings.qdrant_prefer_grpc:
                # 使用gRPC连接
                self.client = QdrantClient(
                    host="localhost",
                    grpc_port=self.settings.qdrant_grpc_port,
                    prefer_grpc=True
                )
                logger.info(f"Qdrant客户端初始化成功 (gRPC端口: {self.settings.qdrant_grpc_port})")
            else:
                # 使用HTTP连接
                self.client = QdrantClient(url=self.settings.qdrant_url)
                logger.info(f"Qdrant客户端初始化成功 (HTTP URL: {self.settings.qdrant_url})")
        except Exception as e:
            logger.error(f"Qdrant客户端初始化失败: {e}")
            raise
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,  # text-embedding-3-small的向量维度
        distance: Distance = Distance.COSINE
    ) -> bool:
        """创建集合"""
        try:
            # 检查集合是否已存在
            collections = self.client.get_collections()
            existing_names = [col.name for col in collections.collections]
            
            if collection_name in existing_names:
                logger.info(f"集合 {collection_name} 已存在")
                return True
            
            # 创建集合
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance)
            )
            logger.info(f"集合 {collection_name} 创建成功")
            return True
        except Exception as e:
            logger.error(f"创建集合失败: {e}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"集合 {collection_name} 删除成功")
            return True
        except Exception as e:
            logger.error(f"删除集合失败: {e}")
            return False
    
    def get_collections(self) -> List[CollectionInfo]:
        """获取所有集合信息"""
        try:
            collections_response = self.client.get_collections()
            collections = []
            
            for collection in collections_response.collections:
                # 获取集合详细信息
                collection_info = self.client.get_collection(collection.name)
                
                collections.append(CollectionInfo(
                    name=collection.name,
                    vectors_count=collection_info.vectors_count or 0,
                    indexed_only=getattr(collection_info, 'indexed_only', False),
                    payload_schema=getattr(collection_info, 'payload_schema', {})
                ))
            
            return collections
        except Exception as e:
            logger.error(f"获取集合列表失败: {e}")
            return []
    
    def upsert_points(
        self,
        collection_name: str,
        points: List[PointStruct]
    ) -> bool:
        """插入或更新向量点"""
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"成功插入 {len(points)} 个向量点到集合 {collection_name}")
            return True
        except Exception as e:
            logger.error(f"插入向量点失败: {e}")
            return False
    
    def search_points(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """搜索相似向量点"""
        try:
            # 构建过滤条件
            query_filter = None
            if filter_conditions:
                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        ) for key, value in filter_conditions.items()
                    ]
                )
            
            # 执行搜索
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # 转换结果格式
            results = []
            for point in search_result:
                results.append({
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload
                })
            
            logger.info(f"搜索完成，返回 {len(results)} 个结果")
            return results
        except Exception as e:
            logger.error(f"搜索向量点失败: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """获取指定集合的信息"""
        try:
            collection_info = self.client.get_collection(collection_name)
            return CollectionInfo(
                name=collection_name,
                vectors_count=collection_info.vectors_count or 0,
                indexed_only=getattr(collection_info, 'indexed_only', False),
                payload_schema=getattr(collection_info, 'payload_schema', {})
            )
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return None
    
    def count_points(self, collection_name: str) -> int:
        """统计集合中的向量点数量"""
        try:
            count_result = self.client.count(collection_name=collection_name)
            return count_result.count
        except Exception as e:
            logger.error(f"统计向量点数量失败: {e}")
            return 0

    def delete_vectors_by_filter(
        self,
        filter_condition: Dict[str, Any],
        collection_name: Optional[str] = None
    ) -> int:
        """根据过滤条件删除向量"""
        try:
            if collection_name is None:
                collection_name = self.settings.qdrant_collection_name

            # 构建Qdrant过滤器
            query_filter = models.Filter(**filter_condition)

            # 先查询匹配的向量数量
            try:
                # 使用scroll方法获取匹配的点，只获取ID
                scroll_result = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=query_filter,
                    limit=10000,  # 设置一个较大的限制
                    with_payload=False,  # 不需要payload，只要ID
                    with_vectors=False   # 不需要向量数据
                )
                points_to_delete = scroll_result[0]  # scroll返回(points, next_page_offset)
                deleted_count = len(points_to_delete)

                if deleted_count == 0:
                    logger.info("没有找到匹配的向量点")
                    return 0

            except Exception as e:
                logger.warning(f"无法查询匹配的向量数量: {e}，将直接执行删除")
                deleted_count = 0

            # 执行删除操作
            delete_result = self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(filter=query_filter)
            )

            # 如果之前无法获取数量，使用删除结果的状态来估计
            if deleted_count == 0:
                # 检查删除操作是否成功
                if hasattr(delete_result, 'status') and delete_result.status == 'completed':
                    deleted_count = 1  # 假设至少删除了一些数据
                else:
                    deleted_count = 0

            logger.info(f"成功删除 {deleted_count} 个向量点")
            return deleted_count

        except Exception as e:
            logger.error(f"删除向量失败: {e}")
            return 0
    
    def close(self):
        """关闭客户端连接"""
        if self.client:
            self.client.close()
            logger.info("Qdrant客户端连接已关闭")


# 创建全局RAG仓库实例
from app.core.config import get_settings
rag_repository = QdrantRepository(get_settings())
