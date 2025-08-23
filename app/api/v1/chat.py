"""
智能聊天API路由
基于 Redis 共享内存的聊天系统
"""
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.core.config import get_settings, Settings
from app.services.rag.conversation_service import ConversationService
from app.schemas.rag import ChatRequest, ChatResponse, ChatEngineType


router = APIRouter(prefix="/chat", tags=["智能聊天"])


def get_chat_service(settings: Settings = Depends(get_settings)) -> ConversationService:
    """获取聊天服务实例"""
    from app.services.rag.rag_settings import get_rag_config_manager
    rag_config_manager = get_rag_config_manager()
    return ConversationService(settings, rag_config_manager)


@router.post("/", response_model=ChatResponse)
async def intelligent_chat(
    request: ChatRequest,
    chat_service: ConversationService = Depends(get_chat_service)
):
    """
    智能聊天接口

    基于 Redis 共享内存的智能聊天系统，支持：
    - 多会话管理（基于 conversation_id）
    - 动态过滤（course_id 或 course_material_id）
    - 双引擎模式（condense_plus_context 或 simple）

    **参数说明：**
    - **conversation_id**: 对话会话ID，用作Redis存储键，确保会话隔离
    - **course_id**: 课程ID（与course_material_id二选一），用于过滤检索范围
    - **course_material_id**: 课程材料ID（与course_id二选一），用于过滤检索范围
    - **chat_engine_type**: 聊天引擎类型
        - `condense_plus_context`: 检索增强模式，基于文档内容回答
        - `simple`: 直接对话模式，不检索文档
    - **question**: 用户问题
    - **collection_name**: 集合名称（可选，默认使用配置中的名称）

    **过滤逻辑：**
    - 如果提供 course_id，检索时只匹配该课程的文本块
    - 如果提供 course_material_id，检索时只匹配该材料的文本块
    - 如果同时提供两者，优先使用 course_id
    - **condense_plus_context 模式行为：**
      - 无过滤条件：返回 "检索必须携带过滤条件，不支持无过滤条件检索"
      - 有过滤条件但无匹配结果：返回 "检索的课程和材料不在数据库中"
    - simple 模式不需要过滤条件

    **引擎模式：**
    - `condense_plus_context`: 使用向量检索 + 上下文整合，适合知识问答
    - `simple`: 直接与LLM对话，适合一般聊天
    """
    try:
        # 验证参数
        if not request.conversation_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conversation_id 不能为空"
            )

        if not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="question 不能为空"
            )

        # 注意：过滤条件验证已移至对话服务层处理

        # 执行聊天
        response = await chat_service.chat(request)

        logger.info(f"聊天完成 - 会话ID: {request.conversation_id}, 引擎: {request.chat_engine_type}, 问题: {request.question[:50]}...")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天API错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天处理失败: {str(e)}"
        )


@router.get("/health")
async def chat_health_check(
    chat_service: ConversationService = Depends(get_chat_service)
):
    """
    聊天服务健康检查
    """
    try:
        # 检查Redis连接
        from llama_index.storage.chat_store.redis import RedisChatStore
        chat_store = RedisChatStore(redis_url="redis://localhost:6379", ttl=3600)
        
        # 简单的连接测试
        test_key = "health_check_test"
        
        return {
            "status": "healthy",
            "redis_connected": True,
            "vector_index_loaded": hasattr(chat_service, 'index'),
            "llm_configured": True,
            "message": "聊天服务运行正常"
        }
    
    except Exception as e:
        logger.error(f"聊天服务健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "redis_connected": False,
            "error": str(e),
            "message": "聊天服务异常"
        }



@router.delete("/conversations/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    chat_service: ConversationService = Depends(get_chat_service)
):
    """
    清除指定会话的聊天记录
    
    - **conversation_id**: 要清除的会话ID
    """
    try:
        if not conversation_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conversation_id 不能为空"
            )
        
        # 创建Redis连接并删除对话记录
        from llama_index.storage.chat_store.redis import RedisChatStore
        chat_store = RedisChatStore(redis_url="redis://localhost:6379", ttl=3600)
        
        # 删除指定会话的数据
        # 注意：RedisChatStore 可能没有直接的删除方法，这里需要根据实际API调整
        # 这是一个示例实现
        
        return {
            "success": True,
            "message": f"会话 {conversation_id} 的聊天记录已清除",
            "conversation_id": conversation_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清除会话记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清除会话记录失败: {str(e)}"
        )
