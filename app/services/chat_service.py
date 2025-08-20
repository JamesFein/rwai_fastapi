"""
智能聊天服务 - 基于Redis共享内存的聊天系统
基于 llama_index_shared_memory_redis_storage.ipynb 的成功实现
"""
import time
from typing import Optional, List
from loguru import logger

# LlamaIndex imports
from llama_index.core import Settings, VectorStoreIndex, PromptTemplate
from llama_index.core.memory import ChatSummaryMemoryBuffer
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.storage.chat_store.redis import RedisChatStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.core.config import Settings as AppSettings
from app.schemas.rag import (
    ChatRequest, ChatResponse, ChatEngineType, SourceInfo
)


class ChatService:
    """智能聊天服务类"""
    
    def __init__(self, settings: AppSettings):
        """初始化聊天服务"""
        self.settings = settings
        self._setup_llama_index()
        self._setup_vector_index()
        self._load_prompts()
    
    def _setup_llama_index(self):
        """设置LlamaIndex全局配置"""
        try:
            # 配置LLM - 与notebook保持一致
            Settings.llm = OpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=self.settings.api_key,
                api_base=self.settings.base_url
            )
            
            # 配置嵌入模型
            Settings.embed_model = OpenAIEmbedding(
                model="text-embedding-3-small",
                api_key=self.settings.api_key,
                api_base=self.settings.base_url
            )
            
            logger.info("LlamaIndex配置完成")
        except Exception as e:
            logger.error(f"LlamaIndex配置失败: {e}")
            raise
    
    def _setup_vector_index(self):
        """设置向量索引 - 连接到现有的Qdrant"""
        try:
            # 连接到本地Qdrant
            qdrant_client = QdrantClient(
                host="localhost",
                port=6334,  # gRPC端口
                prefer_grpc=True,
                timeout=10
            )
            
            # 从已有集合创建向量存储
            collection_name = self.settings.qdrant_collection_name
            vector_store = QdrantVectorStore(collection_name=collection_name, client=qdrant_client)
            
            # 从Qdrant向量存储创建index
            self.index = VectorStoreIndex.from_vector_store(vector_store)
            
            logger.info(f"向量索引加载完成，集合: {collection_name}")
        except Exception as e:
            logger.error(f"向量索引设置失败: {e}")
            raise
    
    def _load_prompts(self):
        """加载提示词模板 - 与notebook保持一致"""
        # 问题压缩提示词
        self.condense_prompt = PromptTemplate(
            "你是一个RAG（检索增强生成）专家，你将根据用户和AI助手之前的聊天历史，把学生最新提出的问题，改写成一个详细完整具体的、携带必要上下文的问题，可以是陈述句也可以疑问句。\n"
            "注意，你改写后的问题将会用于通过向量检索来获取与问题最相关的文本块。\n"
            "=== 聊天历史 ===\n"
            "{chat_history}\n\n"
            "=== 学生最新提出的问题 ===\n"
            "{question}\n\n"
            "=== 改写后的独立问题 ===\n"
        )
        
        # 上下文整合提示词
        self.context_prompt = (
            "你叫做文文，一个专业的热心活泼乐于助人的ai聊天助手，擅长查找学习资料，而且你总是喜欢用理查德·费曼的风格讲解学习资料。你总是用排版清晰的markdown格式回答问题，用很多的emoji让内容更生动。\n\n"
            "📚 **相关文档内容：**\n"
            "{context_str}\n\n"
            "🎯 **回答要求：**\n"
            "1. 严格基于上述文档内容进行回答\n"
            "2. 如果文档内容不足以回答问题，请明确说明'文档中暂无相关信息'\n"
            "3. 回答要条理清晰，使用适当的emoji让内容更生动\n"
            "4. 请引用具体的文档内容来支撑你的回答\n\n"
            "💡 **请基于以上文档和之前的对话历史来回答用户的问题。**"
            "根据以上信息，请回答这个问题: {query_str}\n\n"
            "====================接下来都是历史聊天记录，你关键要找到用户最后问的问题认真回答========================\n\n"
        )
        
        # 摘要提示词
        self.summary_prompt = "你是对话记忆助理。请在 300 字内总结用户问的主要问题，困惑点，以及已经给出的关键信息、结论和思路。"
        
        # Simple引擎的系统提示词
        self.simple_system_prompt = "你叫做文文，一个专业的热心活泼乐于助人的ai聊天助手，擅长查找学习资料，而且你总是喜欢用理查德·费曼的风格讲解学习资料。你总是用排版清晰的markdown格式回答问题，用很多的emoji让内容更生动。"
        
        logger.info("提示词模板加载完成")
    
    def _create_chat_store_and_memory(self, conversation_id: str) -> ChatSummaryMemoryBuffer:
        """创建Redis聊天存储和内存缓冲区"""
        try:
            # 创建Redis聊天存储
            chat_store = RedisChatStore(redis_url="redis://localhost:6379", ttl=3600)
            
            # 创建聊天摘要内存缓冲区
            memory = ChatSummaryMemoryBuffer.from_defaults(
                token_limit=4000,
                llm=Settings.llm,
                chat_store=chat_store,
                chat_store_key=conversation_id,  # 使用用户提供的conversation_id
                summarize_prompt=self.summary_prompt
            )
            
            return memory
        except Exception as e:
            logger.error(f"创建聊天存储和内存失败: {e}")
            raise
    
    def _create_filters(self, course_id: Optional[str], course_material_id: Optional[str]) -> Optional[MetadataFilters]:
        """创建动态过滤器"""
        filters_list = []
        
        # course_id 和 course_material_id 只能存在一个
        if course_id and course_material_id:
            logger.warning("course_id 和 course_material_id 只能选择一个，优先使用 course_id")
            filters_list.append(
                MetadataFilter(key="course_id", value=course_id, operator=FilterOperator.EQ)
            )
        elif course_id:
            filters_list.append(
                MetadataFilter(key="course_id", value=course_id, operator=FilterOperator.EQ)
            )
        elif course_material_id:
            filters_list.append(
                MetadataFilter(key="course_material_id", value=course_material_id, operator=FilterOperator.EQ)
            )
        
        if filters_list:
            return MetadataFilters(filters=filters_list)
        return None
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        start_time = time.time()
        
        try:
            # 创建内存和聊天存储
            memory = self._create_chat_store_and_memory(request.conversation_id)
            
            # 创建过滤器
            filters = self._create_filters(request.course_id, request.course_material_id)
            
            # 生成过滤信息描述
            filter_info = self._get_filter_info(request.course_id, request.course_material_id)
            
            if request.chat_engine_type == ChatEngineType.CONDENSE_PLUS_CONTEXT:
                # 使用condense_plus_context模式
                response = await self._chat_with_condense_plus_context(
                    request.question, memory, filters
                )
            else:
                # 使用simple模式
                response = await self._chat_with_simple_engine(
                    request.question, memory
                )
            
            processing_time = time.time() - start_time
            
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

    async def _chat_with_condense_plus_context(
        self,
        question: str,
        memory: ChatSummaryMemoryBuffer,
        filters: Optional[MetadataFilters]
    ) -> dict:
        """使用condense_plus_context模式进行聊天"""
        try:
            # 创建带过滤器的查询引擎
            if filters:
                query_engine = self.index.as_query_engine(similarity_top_k=6, filters=filters)
            else:
                query_engine = self.index.as_query_engine(similarity_top_k=6)

            # 创建condense_plus_context聊天引擎
            chat_engine = self.index.as_chat_engine(
                chat_mode="condense_plus_context",
                condense_prompt=self.condense_prompt,
                context_prompt=self.context_prompt,
                memory=memory,
                verbose=True,
            )

            # 手动设置过滤器到聊天引擎的查询引擎
            if filters:
                chat_engine._query_engine = query_engine

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
                        course_material_name=metadata.get("course_material_name", ""),
                        chunk_text=content_preview,
                        score=score
                    ))

            return {
                "answer": str(response),
                "sources": sources
            }

        except Exception as e:
            logger.error(f"condense_plus_context聊天失败: {e}")
            raise

    async def _chat_with_simple_engine(
        self,
        question: str,
        memory: ChatSummaryMemoryBuffer
    ) -> dict:
        """使用simple模式进行聊天"""
        try:
            # 创建简单聊天引擎
            chat_engine = SimpleChatEngine.from_defaults(
                llm=Settings.llm,
                memory=memory,
                system_prompt=self.simple_system_prompt,
                verbose=True
            )

            # 执行聊天
            response = chat_engine.chat(question)

            return {
                "answer": str(response),
                "sources": []  # simple模式没有来源
            }

        except Exception as e:
            logger.error(f"simple聊天失败: {e}")
            raise
