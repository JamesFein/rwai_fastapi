"""
智能对话API路由
使用新的对话服务实现，提供更好的架构和功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.core.config import get_settings, Settings
from app.services.rag.conversation_service import ConversationService
from app.services.rag.rag_settings import get_rag_config_manager, RAGConfigManager
from app.schemas.rag import ChatRequest, ChatResponse, ChatEngineType

router = APIRouter(prefix="/conversation", tags=["智能对话"])


def get_conversation_service(
    settings: Settings = Depends(get_settings),
    rag_config_manager: RAGConfigManager = Depends(get_rag_config_manager)
) -> ConversationService:
    """获取对话服务实例"""
    return ConversationService(settings, rag_config_manager)


@router.post("/chat", response_model=ChatResponse)
async def intelligent_chat(
    request: ChatRequest,
    conv_service: ConversationService = Depends(get_conversation_service)
):
    """
    智能对话接口

    基于新架构的智能对话系统，提供更好的性能和功能：

    **新特性：**
    - 模块化架构：分离内存管理和引擎工厂
    - 统一配置管理：通过RAG配置管理器统一管理所有配置
    - 更好的错误处理：详细的错误信息和日志记录
    - 灵活的提示词管理：支持文件化的提示词模板

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
        response = await conv_service.chat(request)

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


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    conv_service: ConversationService = Depends(get_conversation_service)
):
    """
    清除指定会话的聊天记录

    使用新的对话服务实现，提供更可靠的清除功能

    - **conversation_id**: 要清除的会话ID
    """
    try:
        if not conversation_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conversation_id 不能为空"
            )

        # 使用新的对话服务清除会话
        success = await conv_service.clear_conversation(conversation_id)

        if success:
            logger.info(f"会话清除成功: {conversation_id}")
            return {
                "success": True,
                "message": f"会话 {conversation_id} 的聊天记录已清除",
                "conversation_id": conversation_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"清除会话 {conversation_id} 失败"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清除会话记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清除会话记录失败: {str(e)}"
        )


@router.get("/engines")
async def get_available_engines():
    """
    获取可用的聊天引擎类型

    返回详细的引擎信息和配置
    """
    return {
        "engines": [
            {
                "type": ChatEngineType.CONDENSE_PLUS_CONTEXT,
                "name": "检索增强模式",
                "description": "基于文档内容的智能问答，适合知识查询",
                "features": [
                    "向量检索",
                    "上下文整合",
                    "来源追踪",
                    "动态过滤",
                    "问题压缩",
                    "对话记忆"
                ],
                "use_cases": [
                    "课程内容问答",
                    "文档知识查询",
                    "专业领域咨询"
                ]
            },
            {
                "type": ChatEngineType.SIMPLE,
                "name": "直接对话模式",
                "description": "与AI直接对话，不检索文档，适合一般聊天",
                "features": [
                    "快速响应",
                    "对话记忆",
                    "自然交流",
                    "多轮对话"
                ],
                "use_cases": [
                    "一般性聊天",
                    "创意讨论",
                    "问题澄清"
                ]
            }
        ],
        "configuration": {
            "memory_management": "Redis-based chat store",
            "prompt_templates": "File-based templates",
            "vector_search": "Qdrant vector database",
            "llm_backend": "OpenAI compatible API"
        }
    }


@router.get("/health")
async def conversation_health_check(
    conv_service: ConversationService = Depends(get_conversation_service)
):
    """
    对话服务健康检查

    提供详细的服务状态信息
    """
    try:
        service_status = conv_service.get_service_status()

        return {
            "status": "healthy",
            "service_info": service_status,
            "message": "对话服务运行正常"
        }

    except Exception as e:
        logger.error(f"对话服务健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "对话服务异常"
        }


@router.get("/conversations/{conversation_id}/status")
async def get_conversation_status(
    conversation_id: str,
    conv_service: ConversationService = Depends(get_conversation_service)
):
    """
    获取指定会话的状态信息

    - **conversation_id**: 会话ID
    """
    try:
        if not conversation_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conversation_id 不能为空"
            )

        # 这里可以添加获取会话状态的逻辑
        # 目前返回基本信息
        return {
            "conversation_id": conversation_id,
            "status": "active",
            "message": "会话状态正常"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话状态失败: {str(e)}"
        )


@router.get("/config")
async def get_conversation_config(
    conv_service: ConversationService = Depends(get_conversation_service)
):
    """
    获取对话服务配置信息

    返回当前的配置设置
    """
    try:
        service_status = conv_service.get_service_status()

        return {
            "configuration": service_status.get("rag_config", {}),
            "components": service_status.get("components", {}),
            "supported_engines": service_status.get("supported_engines", [])
        }

    except Exception as e:
        logger.error(f"获取对话配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话配置失败: {str(e)}"
        )