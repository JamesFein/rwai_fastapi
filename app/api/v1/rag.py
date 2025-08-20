"""
RAG模块API路由

⚠️ DEPRECATED: 此API版本已被标记为过时，请使用 /api/v1/rag/v2 新版本API。
新版本提供更好的性能、错误处理和功能。
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import get_settings, Settings
from app.services.rag_service import RAGService
from app.schemas.rag import (
    IndexRequest, IndexResponse, QueryRequest, QueryResponse,
    CollectionListResponse, DeleteCollectionResponse, DocumentMetadata
)

router = APIRouter(prefix="/rag", tags=["RAG (Deprecated)"])


def _log_deprecated_warning(endpoint_name: str):
    """记录deprecated警告"""
    logger.warning(f"⚠️ DEPRECATED API调用: {endpoint_name} - 请使用 /api/v1/rag/v2 新版本API")


def get_rag_service(settings: Settings = Depends(get_settings)) -> RAGService:
    """获取RAG服务实例"""
    return RAGService(settings)


@router.post("/index", response_model=IndexResponse, deprecated=True)
async def build_index(
    file: UploadFile = File(...),
    course_id: str = Form(...),
    course_material_id: str = Form(...),
    course_material_name: str = Form(...),
    collection_name: str = Form(None),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    建立文档索引

    ⚠️ DEPRECATED: 请使用 /api/v1/rag/v2/index 新版本API

    - **file**: 上传的MD文件
    - **course_id**: 课程ID
    - **course_material_id**: 课程材料ID
    - **course_material_name**: 课程材料名称
    - **collection_name**: 集合名称（可选，默认使用配置中的名称）
    """
    try:
        _log_deprecated_warning("POST /rag/index")
        # 验证文件类型
        if not file.filename.endswith(('.md', '.txt')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持.md和.txt文件"
            )
        
        # 读取文件内容
        file_content = await file.read()
        content_str = file_content.decode('utf-8')
        
        # 构建请求对象
        metadata = DocumentMetadata(
            course_id=course_id,
            course_material_id=course_material_id,
            course_material_name=course_material_name,
            file_path=file.filename,
            file_size=len(file_content)
        )
        
        request = IndexRequest(
            file_content=content_str,
            metadata=metadata,
            collection_name=collection_name
        )
        
        # 执行索引建立
        response = await rag_service.build_index(request)
        
        if response.success:
            logger.info(f"索引建立成功: {file.filename}")
            return response
        else:
            logger.error(f"索引建立失败: {response.message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"索引建立API错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"索引建立失败: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse, deprecated=True)
async def query_rag(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    RAG问答查询

    ⚠️ DEPRECATED: 请使用 /api/v1/conversation/v2/chat 新版本API

    - **question**: 用户问题
    - **mode**: 聊天模式（query: 检索模式, chat: 直接聊天模式）
    - **course_id**: 课程ID（可选，用于过滤检索范围）
    - **chat_memory**: 聊天记忆（可选）
    - **collection_name**: 集合名称（可选）
    - **top_k**: 检索Top-K数量（可选）
    """
    try:
        _log_deprecated_warning("POST /rag/query")
        # 执行查询
        response = await rag_service.query(request)
        
        logger.info(f"查询完成: {request.question[:50]}...")
        return response
    
    except Exception as e:
        logger.error(f"查询API错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.get("/collections", response_model=CollectionListResponse)
async def get_collections(
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    获取所有集合列表
    """
    try:
        collections = await rag_service.qdrant_repo.get_collections()
        
        return CollectionListResponse(
            collections=collections,
            total_count=len(collections)
        )
    
    except Exception as e:
        logger.error(f"获取集合列表API错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取集合列表失败: {str(e)}"
        )


@router.delete("/collections/{collection_name}", response_model=DeleteCollectionResponse)
async def delete_collection(
    collection_name: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    删除指定集合
    
    - **collection_name**: 要删除的集合名称
    """
    try:
        success = await rag_service.qdrant_repo.delete_collection(collection_name)
        
        if success:
            return DeleteCollectionResponse(
                success=True,
                message=f"集合 {collection_name} 删除成功",
                collection_name=collection_name
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除集合 {collection_name} 失败"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除集合API错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除集合失败: {str(e)}"
        )


@router.get("/collections/{collection_name}/info")
async def get_collection_info(
    collection_name: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    获取指定集合的详细信息
    
    - **collection_name**: 集合名称
    """
    try:
        collection_info = await rag_service.qdrant_repo.get_collection_info(collection_name)
        
        if collection_info:
            return collection_info
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"集合 {collection_name} 不存在"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取集合信息API错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取集合信息失败: {str(e)}"
        )


@router.get("/health")
async def health_check(
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    RAG服务健康检查
    """
    try:
        # 检查Qdrant连接
        collections = await rag_service.qdrant_repo.get_collections()
        
        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collections_count": len(collections),
            "message": "RAG服务运行正常"
        }
    
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "qdrant_connected": False,
                "error": str(e),
                "message": "RAG服务异常"
            }
        )
