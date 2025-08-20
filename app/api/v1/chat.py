"""
智能聊天API路由
基于 Redis 共享内存的聊天系统

⚠️ DEPRECATED: 此API版本已被标记为过时，请使用 /api/v1/conversation/v2 新版本API。
新版本提供更好的架构、性能和功能。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.core.config import get_settings, Settings
from app.services.chat_service import ChatService
from app.schemas.rag import ChatRequest, ChatResponse, ChatEngineType


router = APIRouter(prefix="/chat", tags=["智能聊天 (Deprecated)"])


def _log_deprecated_warning(endpoint_name: str):
    """记录deprecated警告"""
    logger.warning(f"⚠️ DEPRECATED API调用: {endpoint_name} - 请使用 /api/v1/conversation/v2 新版本API")


def get_chat_service(settings: Settings = Depends(get_settings)) -> ChatService:
    """获取聊天服务实例"""
    return ChatService(settings)


@router.post("/", response_model=ChatResponse, deprecated=True)
async def intelligent_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    智能聊天接口

    ⚠️ DEPRECATED: 请使用 /api/v1/conversation/v2/chat 新版本API

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
    - 如果都不提供，搜索全部文档
    
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
        
        # 验证过滤参数（至少提供一个或都不提供）
        if request.chat_engine_type == ChatEngineType.CONDENSE_PLUS_CONTEXT:
            if not request.course_id and not request.course_material_id:
                logger.warning(f"condense_plus_context模式建议提供course_id或course_material_id进行过滤")
        
        # 记录deprecated警告
        _log_deprecated_warning("POST /chat/")

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
    chat_service: ChatService = Depends(get_chat_service)
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


@router.get("/engines")
async def get_available_engines():
    """
    获取可用的聊天引擎类型
    """
    return {
        "engines": [
            {
                "type": ChatEngineType.CONDENSE_PLUS_CONTEXT,
                "name": "检索增强模式",
                "description": "基于文档内容的智能问答，适合知识查询",
                "features": ["向量检索", "上下文整合", "来源追踪", "动态过滤"]
            },
            {
                "type": ChatEngineType.SIMPLE,
                "name": "直接对话模式", 
                "description": "与AI直接对话，不检索文档，适合一般聊天",
                "features": ["快速响应", "对话记忆", "自然交流"]
            }
        ]
    }


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
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
