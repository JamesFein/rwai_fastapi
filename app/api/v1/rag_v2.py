"""
RAG模块API路由 v2
使用新的文档索引服务实现
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import get_settings, Settings
from app.services.rag.document_indexing_service import DocumentIndexingService
from app.services.rag.rag_settings import get_rag_config_manager, RAGConfigManager
from app.schemas.rag import (
    IndexRequest, IndexResponse, CollectionInfo,
    DocumentMetadata, DeleteCollectionResponse
)

router = APIRouter(prefix="/rag/v2", tags=["RAG v2"])


def get_document_indexing_service(
    settings: Settings = Depends(get_settings),
    rag_config_manager: RAGConfigManager = Depends(get_rag_config_manager)
) -> DocumentIndexingService:
    """获取文档索引服务实例"""
    return DocumentIndexingService(settings, rag_config_manager)


@router.post("/index", response_model=IndexResponse)
async def build_index(
    file: UploadFile = File(...),
    course_id: str = Form(...),
    course_material_id: str = Form(...),
    course_material_name: str = Form(...),
    collection_name: Optional[str] = Form(None),
    doc_service: DocumentIndexingService = Depends(get_document_indexing_service)
):
    """
    建立文档索引 v2
    
    使用新的文档索引服务实现，提供更好的性能和错误处理
    
    - **file**: 上传的MD文件
    - **course_id**: 课程ID
    - **course_material_id**: 课程材料ID
    - **course_material_name**: 课程材料名称
    - **collection_name**: 集合名称（可选，默认使用配置中的名称）
    """
    try:
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
        response = await doc_service.build_index(request)
        
        if response.success:
            logger.info(f"索引建立成功 v2: {file.filename}")
            return response
        else:
            logger.error(f"索引建立失败 v2: {response.message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"索引建立API错误 v2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"索引建立失败: {str(e)}"
        )


@router.get("/collections", response_model=List[CollectionInfo])
def get_collections(
    doc_service: DocumentIndexingService = Depends(get_document_indexing_service)
):
    """
    获取所有集合列表 v2

    返回详细的集合信息，包括向量数量等统计信息
    """
    try:
        collections = doc_service.get_collections()
        logger.info(f"获取集合列表成功 v2: {len(collections)} 个集合")
        return collections

    except Exception as e:
        logger.error(f"获取集合列表API错误 v2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取集合列表失败: {str(e)}"
        )


@router.get("/collections/{collection_name}", response_model=CollectionInfo)
def get_collection_info(
    collection_name: str,
    doc_service: DocumentIndexingService = Depends(get_document_indexing_service)
):
    """
    获取指定集合的详细信息 v2

    - **collection_name**: 集合名称
    """
    try:
        collection_info = doc_service.get_collection_info(collection_name)
        
        if collection_info:
            logger.info(f"获取集合信息成功 v2: {collection_name}")
            return collection_info
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"集合 {collection_name} 不存在"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取集合信息API错误 v2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取集合信息失败: {str(e)}"
        )


@router.delete("/collections/{collection_name}", response_model=DeleteCollectionResponse)
def delete_collection(
    collection_name: str,
    doc_service: DocumentIndexingService = Depends(get_document_indexing_service)
):
    """
    删除指定集合 v2

    - **collection_name**: 要删除的集合名称
    """
    try:
        success = doc_service.delete_collection(collection_name)
        
        if success:
            logger.info(f"集合删除成功 v2: {collection_name}")
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
        logger.error(f"删除集合API错误 v2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除集合失败: {str(e)}"
        )


@router.delete("/documents/course/{course_id}")
def delete_documents_by_course(
    course_id: str,
    collection_name: Optional[str] = None,
    doc_service: DocumentIndexingService = Depends(get_document_indexing_service)
):
    """
    删除指定课程的所有文档 v2

    - **course_id**: 课程ID
    - **collection_name**: 集合名称（可选）
    """
    try:
        deleted_count = doc_service.delete_documents_by_course(
            course_id, collection_name
        )
        
        logger.info(f"课程文档删除成功 v2: 课程ID={course_id}, 删除数量={deleted_count}")
        return {
            "success": True,
            "message": f"成功删除课程 {course_id} 的 {deleted_count} 个文档",
            "course_id": course_id,
            "deleted_count": deleted_count,
            "collection_name": collection_name
        }
    
    except Exception as e:
        logger.error(f"删除课程文档API错误 v2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除课程文档失败: {str(e)}"
        )


@router.delete("/documents/material/{course_id}/{course_material_id}")
def delete_documents_by_material(
    course_id: str,
    course_material_id: str,
    collection_name: Optional[str] = None,
    doc_service: DocumentIndexingService = Depends(get_document_indexing_service)
):
    """
    删除指定课程材料的所有文档 v2

    - **course_id**: 课程ID
    - **course_material_id**: 课程材料ID
    - **collection_name**: 集合名称（可选）
    """
    try:
        deleted_count = doc_service.delete_documents_by_material(
            course_id, course_material_id, collection_name
        )
        
        logger.info(f"课程材料文档删除成功 v2: 材料ID={course_material_id}, 删除数量={deleted_count}")
        return {
            "success": True,
            "message": f"成功删除课程材料 {course_material_id} 的 {deleted_count} 个文档",
            "course_id": course_id,
            "course_material_id": course_material_id,
            "deleted_count": deleted_count,
            "collection_name": collection_name
        }
    
    except Exception as e:
        logger.error(f"删除课程材料文档API错误 v2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除课程材料文档失败: {str(e)}"
        )


@router.get("/collections/{collection_name}/count")
def count_documents(
    collection_name: str,
    doc_service: DocumentIndexingService = Depends(get_document_indexing_service)
):
    """
    统计集合中的文档数量 v2

    - **collection_name**: 集合名称
    """
    try:
        count = doc_service.count_documents(collection_name)
        
        logger.info(f"文档数量统计成功 v2: 集合={collection_name}, 数量={count}")
        return {
            "collection_name": collection_name,
            "document_count": count
        }
    
    except Exception as e:
        logger.error(f"统计文档数量API错误 v2: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"统计文档数量失败: {str(e)}"
        )


@router.get("/health")
async def health_check(
    doc_service: DocumentIndexingService = Depends(get_document_indexing_service)
):
    """
    RAG服务健康检查 v2
    
    提供详细的服务状态信息
    """
    try:
        service_status = doc_service.get_service_status()
        
        return {
            "status": "healthy",
            "version": "v2",
            "service_info": service_status,
            "message": "RAG服务 v2 运行正常"
        }
    
    except Exception as e:
        logger.error(f"健康检查失败 v2: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "version": "v2",
                "error": str(e),
                "message": "RAG服务 v2 异常"
            }
        )
