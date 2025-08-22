"""
对话服务
负责对话内存管理、聊天引擎工厂、智能聊天处理
"""
import time
from typing import Optional, List, Dict, Any
from pathlib import Path
from loguru import logger

# LlamaIndex imports
from llama_index.core import Settings, VectorStoreIndex, PromptTemplate
from llama_index.core.memory import ChatSummaryMemoryBuffer
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.storage.chat_store.redis import RedisChatStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.core.config import Settings as AppSettings
from app.services.rag.rag_settings import RAGConfigManager
from app.schemas.rag import (
    ChatRequest, ChatResponse, ChatEngineType, SourceInfo
)


class ConversationMemoryManager:
    """对话内存管理器"""
    
    def __init__(self, rag_config_manager: RAGConfigManager):
        """
        初始化对话内存管理器
        
        Args:
            rag_config_manager: RAG配置管理器
        """
        self.rag_config_manager = rag_config_manager
        self._load_prompts()
    
    def _load_prompts(self):
        """加载提示词模板"""
        try:
            prompts_dir = Path("app/prompts")
            
            # 加载聊天摘要提示词
            with open(prompts_dir / "chat_summary.txt", "r", encoding="utf-8") as f:
                self.summary_prompt = f.read().strip()
            
            logger.info("对话提示词模板加载完成")
        except Exception as e:
            logger.error(f"对话提示词模板加载失败: {e}")
            # 使用默认提示词
            self.summary_prompt = "你是对话记忆助理。请在 300 字内总结用户问的主要问题，困惑点，以及已经给出的关键信息、结论和思路。"
    
    def create_memory(self, conversation_id: str) -> ChatSummaryMemoryBuffer:
        """
        创建Redis聊天存储和内存缓冲区
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            聊天摘要内存缓冲区
        """
        try:
            # 获取Redis配置
            redis_config = self.rag_config_manager.get_redis_config()
            
            # 创建Redis聊天存储
            chat_store = RedisChatStore(
                redis_url=redis_config["redis_url"], 
                ttl=redis_config["ttl"]
            )
            
            # 获取对话配置
            conversation_config = self.rag_config_manager.get_conversation_config()
            
            # 创建聊天摘要内存缓冲区
            memory = ChatSummaryMemoryBuffer.from_defaults(
                token_limit=conversation_config["token_limit"],
                llm=Settings.llm,
                chat_store=chat_store,
                chat_store_key=conversation_id,
                summarize_prompt=self.summary_prompt
            )
            
            logger.info(f"对话内存创建成功 - 对话ID: {conversation_id}")
            return memory
        except Exception as e:
            logger.error(f"创建聊天存储和内存失败: {e}")
            raise
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        清除指定对话的内存
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            清除是否成功
        """
        try:
            # 获取Redis配置
            redis_config = self.rag_config_manager.get_redis_config()
            
            # 创建Redis聊天存储
            chat_store = RedisChatStore(
                redis_url=redis_config["redis_url"], 
                ttl=redis_config["ttl"]
            )
            
            # 删除对话记录
            chat_store.delete_messages(conversation_id)
            
            logger.info(f"对话内存清除成功 - 对话ID: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"清除对话内存失败: {e}")
            return False


class ChatEngineFactory:
    """聊天引擎工厂"""
    
    def __init__(self, app_settings: AppSettings, rag_config_manager: RAGConfigManager):
        """
        初始化聊天引擎工厂
        
        Args:
            app_settings: 应用配置
            rag_config_manager: RAG配置管理器
        """
        self.app_settings = app_settings
        self.rag_config_manager = rag_config_manager
        self.index = None
        self._setup_vector_index()
        self._load_prompts()
    
    def _setup_vector_index(self):
        """设置向量索引 - 连接到现有的Qdrant"""
        try:
            # 获取Qdrant配置
            qdrant_config = self.rag_config_manager.get_qdrant_config()
            
            # 连接到Qdrant
            qdrant_client = QdrantClient(
                host=qdrant_config["host"],
                port=qdrant_config["port"],
                prefer_grpc=qdrant_config["prefer_grpc"],
                timeout=qdrant_config["timeout"]
            )
            
            # 从已有集合创建向量存储
            collection_name = self.app_settings.qdrant_collection_name
            vector_store = QdrantVectorStore(collection_name=collection_name, client=qdrant_client)
            
            # 从Qdrant向量存储创建index
            self.index = VectorStoreIndex.from_vector_store(vector_store)
            
            logger.info(f"向量索引加载完成，集合: {collection_name}")
        except Exception as e:
            logger.error(f"向量索引设置失败: {e}")
            raise
    
    def _load_prompts(self):
        """加载提示词模板"""
        try:
            prompts_dir = Path("app/prompts")
            
            # 加载问题压缩提示词
            with open(prompts_dir / "condense_question.txt", "r", encoding="utf-8") as f:
                condense_prompt_text = f.read().strip()
            
            self.condense_prompt = PromptTemplate(condense_prompt_text)
            
            # 加载上下文整合提示词
            with open(prompts_dir / "context_integration.txt", "r", encoding="utf-8") as f:
                self.context_prompt = f.read().strip()
            
            # 加载简单聊天系统提示词
            with open(prompts_dir / "simple_system.txt", "r", encoding="utf-8") as f:
                self.simple_system_prompt = f.read().strip()
            
            logger.info("聊天引擎提示词模板加载完成")
        except Exception as e:
            logger.error(f"聊天引擎提示词模板加载失败: {e}")
            # 使用默认提示词
            self.condense_prompt = PromptTemplate(
                "你是一个RAG专家，将根据聊天历史把最新问题改写成独立问题。\n"
                "聊天历史：{chat_history}\n"
                "最新问题：{question}\n"
                "独立问题："
            )
            self.context_prompt = (
                "基于以下文档内容回答问题：\n{context_str}\n"
                "问题：{query_str}\n"
            )
            self.simple_system_prompt = "你是一个友好的AI助手。"
    
    def create_engine(
        self, 
        engine_type: ChatEngineType, 
        memory: ChatSummaryMemoryBuffer,
        filters: Optional[MetadataFilters] = None
    ):
        """
        创建聊天引擎
        
        Args:
            engine_type: 引擎类型
            memory: 对话内存
            filters: 元数据过滤器
            
        Returns:
            聊天引擎实例
        """
        try:
            if engine_type == ChatEngineType.CONDENSE_PLUS_CONTEXT:
                return self._create_condense_plus_context_engine(memory, filters)
            else:
                return self._create_simple_engine(memory)
        except Exception as e:
            logger.error(f"创建聊天引擎失败: {e}")
            raise
    
    def _create_condense_plus_context_engine(
        self,
        memory: ChatSummaryMemoryBuffer,
        filters: Optional[MetadataFilters] = None
    ):
        """创建condense_plus_context聊天引擎"""
        try:
            # 获取对话配置
            conversation_config = self.rag_config_manager.get_conversation_config()

            # 创建condense_plus_context聊天引擎，直接传递过滤器参数
            if filters:
                chat_engine = self.index.as_chat_engine(
                    chat_mode="condense_plus_context",
                    condense_prompt=self.condense_prompt,
                    context_prompt=self.context_prompt,
                    memory=memory,
                    verbose=True,
                    similarity_top_k=conversation_config["similarity_top_k"],
                    filters=filters  # 直接传递过滤器
                )
                logger.info(f"condense_plus_context聊天引擎创建成功，使用过滤器: {filters}")
            else:
                chat_engine = self.index.as_chat_engine(
                    chat_mode="condense_plus_context",
                    condense_prompt=self.condense_prompt,
                    context_prompt=self.context_prompt,
                    memory=memory,
                    verbose=True,
                    similarity_top_k=conversation_config["similarity_top_k"]
                )
                logger.info("condense_plus_context聊天引擎创建成功，无过滤器")

            return chat_engine
        except Exception as e:
            logger.error(f"创建condense_plus_context聊天引擎失败: {e}")
            raise
    
    def _create_simple_engine(self, memory: ChatSummaryMemoryBuffer):
        """创建simple聊天引擎"""
        try:
            # 创建简单聊天引擎
            chat_engine = SimpleChatEngine.from_defaults(
                llm=Settings.llm,
                memory=memory,
                system_prompt=self.simple_system_prompt,
                verbose=True
            )

            logger.info("simple聊天引擎创建成功")
            return chat_engine
        except Exception as e:
            logger.error(f"创建simple聊天引擎失败: {e}")
            raise


class ConversationService:
    """对话服务类"""
    
    def __init__(self, app_settings: AppSettings, rag_config_manager: RAGConfigManager):
        """
        初始化对话服务
        
        Args:
            app_settings: 应用配置
            rag_config_manager: RAG配置管理器
        """
        self.app_settings = app_settings
        self.rag_config_manager = rag_config_manager
        
        # 确保RAG配置已初始化
        if not rag_config_manager.rag_settings:
            rag_config_manager.initialize(app_settings)
        
        # 初始化组件
        self.memory_manager = ConversationMemoryManager(rag_config_manager)
        self.engine_factory = ChatEngineFactory(app_settings, rag_config_manager)
    
    def _create_filters(self, course_id: Optional[str], course_material_id: Optional[str]) -> Optional[MetadataFilters]:
        """创建动态过滤器"""
        filters_list = []

        # course_id 和 course_material_id 只能存在一个
        if course_id and course_material_id:
            logger.warning("course_id 和 course_material_id 只能选择一个，优先使用 course_id")
            filters_list.append(
                MetadataFilter(key="course_id", value=course_id, operator=FilterOperator.EQ)
            )
            logger.info(f"创建过滤器: course_id = {course_id} (优先使用)")
        elif course_id:
            filters_list.append(
                MetadataFilter(key="course_id", value=course_id, operator=FilterOperator.EQ)
            )
            logger.info(f"创建过滤器: course_id = {course_id}")
        elif course_material_id:
            filters_list.append(
                MetadataFilter(key="course_material_id", value=course_material_id, operator=FilterOperator.EQ)
            )
            logger.info(f"创建过滤器: course_material_id = {course_material_id}")

        if filters_list:
            metadata_filters = MetadataFilters(filters=filters_list)
            logger.info(f"过滤器创建成功: {metadata_filters}")
            return metadata_filters
        else:
            logger.info("未创建过滤器，将搜索全部文档")
            return None

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        处理聊天请求

        Args:
            request: 聊天请求

        Returns:
            聊天响应
        """
        start_time = time.time()

        try:
            logger.info(f"处理聊天请求 - 对话ID: {request.conversation_id}, 引擎类型: {request.chat_engine_type}")

            # 创建过滤器
            filters = self._create_filters(request.course_id, request.course_material_id)

            # 对于condense_plus_context模式，强制要求过滤条件
            if request.chat_engine_type == ChatEngineType.CONDENSE_PLUS_CONTEXT:
                if filters is None:
                    # 没有过滤条件，直接返回错误信息
                    processing_time = time.time() - start_time
                    logger.warning("condense_plus_context模式必须提供过滤条件")
                    return ChatResponse(
                        answer="检索必须携带过滤条件，不支持无过滤条件检索",
                        sources=[],
                        conversation_id=request.conversation_id,
                        chat_engine_type=request.chat_engine_type,
                        filter_info="检索必须携带过滤条件，不支持无过滤条件检索",
                        processing_time=processing_time
                    )

            # 创建内存和聊天存储
            memory = self.memory_manager.create_memory(request.conversation_id)

            # 生成过滤信息描述
            filter_info = self._get_filter_info(request.course_id, request.course_material_id)

            # 创建聊天引擎
            chat_engine = self.engine_factory.create_engine(
                request.chat_engine_type, memory, filters
            )

            # 执行聊天
            if request.chat_engine_type == ChatEngineType.CONDENSE_PLUS_CONTEXT:
                response = await self._chat_with_condense_plus_context(
                    request.question, chat_engine, filters
                )
            else:
                response = await self._chat_with_simple_engine(
                    request.question, chat_engine
                )

            processing_time = time.time() - start_time

            logger.info(f"聊天处理完成 - 对话ID: {request.conversation_id}, 耗时: {processing_time:.2f}s")

            # 如果检索结果为空且有过滤条件，更新filter_info
            if (response["answer"] == "检索的课程和材料不在数据库中" and
                request.chat_engine_type == ChatEngineType.CONDENSE_PLUS_CONTEXT):
                filter_info = "检索的课程和材料不在数据库中"

            return ChatResponse(
                answer=response["answer"],
                sources=response.get("sources", []),
                conversation_id=request.conversation_id,
                chat_engine_type=request.chat_engine_type,
                filter_info=filter_info,
                processing_time=processing_time
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"聊天处理失败: {e}")
            return ChatResponse(
                answer=f"抱歉，处理您的问题时出现错误: {str(e)}",
                sources=[],
                conversation_id=request.conversation_id,
                chat_engine_type=request.chat_engine_type,
                filter_info=self._get_filter_info(request.course_id, request.course_material_id),
                processing_time=processing_time
            )

    def _get_filter_info(self, course_id: Optional[str], course_material_id: Optional[str]) -> str:
        """获取过滤条件信息描述"""
        if course_id and course_material_id:
            return f"course_id = {course_id} (优先使用)"
        elif course_id:
            return f"course_id = {course_id}"
        elif course_material_id:
            return f"course_material_id = {course_material_id}"
        else:
            return "无过滤条件，搜索全部文档"

    async def _chat_with_condense_plus_context(self, question: str, chat_engine, filters=None) -> dict:
        """使用condense_plus_context模式进行聊天"""
        try:
            # 执行聊天
            response = chat_engine.chat(question)

            # 提取来源信息
            sources = []
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for source_node in response.source_nodes:
                    metadata = source_node.node.metadata
                    content = source_node.node.get_content().strip()

                    # 限制内容预览长度
                    if len(content) > 200:
                        content_preview = content[:200] + "..."
                    else:
                        content_preview = content

                    score = getattr(source_node, 'score', 0.0)

                    sources.append(SourceInfo(
                        course_id=metadata.get("course_id", ""),
                        course_material_id=metadata.get("course_material_id", ""),
                        chunk_text=content_preview,
                        score=score
                    ))
            else:
                # 如果有过滤条件但没有检索到任何文档，返回特定错误信息
                if filters is not None:
                    logger.warning("有过滤条件但未检索到匹配的文档")
                    return {
                        "answer": "检索的课程和材料不在数据库中",
                        "sources": []
                    }

            return {
                "answer": str(response),
                "sources": sources
            }

        except Exception as e:
            logger.error(f"condense_plus_context聊天失败: {e}")
            raise

    async def _chat_with_simple_engine(self, question: str, chat_engine) -> dict:
        """使用simple模式进行聊天"""
        try:
            # 执行聊天
            response = chat_engine.chat(question)

            return {
                "answer": str(response),
                "sources": []  # simple模式没有来源
            }

        except Exception as e:
            logger.error(f"simple聊天失败: {e}")
            raise

    async def clear_conversation(self, conversation_id: str) -> bool:
        """
        清除指定对话的内存

        Args:
            conversation_id: 对话ID

        Returns:
            清除是否成功
        """
        try:
            logger.info(f"清除对话 - 对话ID: {conversation_id}")
            success = self.memory_manager.clear_conversation(conversation_id)
            if success:
                logger.info(f"对话清除成功 - 对话ID: {conversation_id}")
            else:
                logger.error(f"对话清除失败 - 对话ID: {conversation_id}")
            return success
        except Exception as e:
            logger.error(f"清除对话异常: {e}")
            return False

    def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态信息

        Returns:
            服务状态字典
        """
        try:
            rag_settings_summary = self.rag_config_manager.get_settings_summary()

            return {
                "service_name": "ConversationService",
                "status": "healthy",
                "rag_config": rag_settings_summary,
                "components": {
                    "memory_manager": "ConversationMemoryManager",
                    "engine_factory": "ChatEngineFactory"
                },
                "supported_engines": [
                    "condense_plus_context",
                    "simple"
                ]
            }
        except Exception as e:
            return {
                "service_name": "ConversationService",
                "status": "error",
                "error": str(e)
            }
