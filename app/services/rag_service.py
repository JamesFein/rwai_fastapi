"""
RAG服务核心 - 负责文档处理、索引建立和问答查询
"""
import time
import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path
from loguru import logger

# LlamaIndex imports
from llama_index.core import Settings, VectorStoreIndex, Document, PromptTemplate
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.memory import ChatSummaryMemoryBuffer
from llama_index.core.chat_engine import SimpleChatEngine, CondensePlusContextChatEngine
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client.http.models import PointStruct

from app.core.config import Settings as AppSettings
from app.repositories.rag_repository import QdrantRepository
from app.schemas.rag import (
    IndexRequest, IndexResponse, QueryRequest, QueryResponse,
    ChatMessage, ChatMemory, SourceInfo, ChatMode
)


class RAGService:
    """RAG服务类"""
    
    def __init__(self, settings: AppSettings):
        """初始化RAG服务"""
        self.settings = settings
        self.qdrant_repo = QdrantRepository(settings)
        self._setup_llama_index()
        self._load_prompts()
    
    def _setup_llama_index(self):
        """设置LlamaIndex全局配置"""
        try:
            # 配置LLM
            Settings.llm = OpenAI(
                model=self.settings.rag_llm_model,
                api_key=self.settings.api_key,
                api_base=self.settings.base_url,
                temperature=0.1
            )
            
            # 配置嵌入模型
            Settings.embed_model = OpenAIEmbedding(
                model=self.settings.rag_embed_model,
                api_key=self.settings.api_key,
                api_base=self.settings.base_url
            )
            
            # 配置文本分块器
            self.text_splitter = SentenceSplitter(
                chunk_size=self.settings.rag_chunk_size,
                chunk_overlap=self.settings.rag_chunk_overlap
            )
            
            logger.info("LlamaIndex配置完成")
        except Exception as e:
            logger.error(f"LlamaIndex配置失败: {e}")
            raise
    
    def _load_prompts(self):
        """加载提示词模板"""
        try:
            prompts_dir = Path("app/prompts")
            
            # 加载RAG系统提示词
            with open(prompts_dir / "rag_system_prompt.txt", "r", encoding="utf-8") as f:
                self.rag_system_prompt = f.read().strip()
            
            # 加载聊天摘要提示词
            with open(prompts_dir / "chat_summary_prompt.txt", "r", encoding="utf-8") as f:
                self.chat_summary_prompt = f.read().strip()
            
            # 加载问题压缩提示词
            with open(prompts_dir / "condense_question_prompt.txt", "r", encoding="utf-8") as f:
                self.condense_question_prompt = f.read().strip()
            
            logger.info("提示词模板加载完成")
        except Exception as e:
            logger.error(f"提示词模板加载失败: {e}")
            raise
    
    async def build_index(self, request: IndexRequest) -> IndexResponse:
        """建立文档索引"""
        start_time = time.time()
        
        try:
            # 使用指定的集合名称或默认名称
            collection_name = request.collection_name or self.settings.qdrant_collection_name
            
            # 确保集合存在
            await self.qdrant_repo.create_collection(collection_name)
            
            # 创建文档对象
            document = Document(
                text=request.file_content,
                metadata={
                    "course_id": request.metadata.course_id,
                    "course_material_id": request.metadata.course_material_id,
                    "course_material_name": request.metadata.course_material_name,
                    "file_path": request.metadata.file_path,
                    "file_size": request.metadata.file_size,
                    "upload_time": request.metadata.upload_time
                }
            )
            
            # 文本分块
            nodes = self.text_splitter.get_nodes_from_documents([document])
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
                        "chunk_index": i
                    }
                )
                points.append(point)
            
            # 批量插入向量点
            success = await self.qdrant_repo.upsert_points(collection_name, points)
            
            processing_time = time.time() - start_time
            
            if success:
                return IndexResponse(
                    success=True,
                    message="索引建立成功",
                    document_count=1,
                    chunk_count=len(nodes),
                    processing_time=processing_time,
                    collection_name=collection_name
                )
            else:
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
            logger.error(f"索引建立失败: {e}")
            return IndexResponse(
                success=False,
                message=f"索引建立失败: {str(e)}",
                document_count=0,
                chunk_count=0,
                processing_time=processing_time,
                collection_name=request.collection_name or self.settings.qdrant_collection_name
            )

    async def query(self, request: QueryRequest) -> QueryResponse:
        """处理问答查询"""
        start_time = time.time()

        try:
            collection_name = request.collection_name or self.settings.qdrant_collection_name
            top_k = request.top_k or self.settings.rag_top_k

            if request.mode == ChatMode.QUERY:
                # 检索模式：使用向量检索
                response = await self._query_with_retrieval(
                    request.question,
                    collection_name,
                    top_k,
                    request.course_id,
                    request.chat_memory
                )
            else:
                # 直接聊天模式：不检索知识库
                response = await self._query_direct_chat(
                    request.question,
                    request.chat_memory
                )

            processing_time = time.time() - start_time
            response.processing_time = processing_time
            response.mode = request.mode

            return response

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"查询处理失败: {e}")
            return QueryResponse(
                answer=f"抱歉，处理您的问题时出现错误: {str(e)}",
                sources=[],
                chat_memory=request.chat_memory,
                mode=request.mode,
                processing_time=processing_time
            )

    async def _query_with_retrieval(
        self,
        question: str,
        collection_name: str,
        top_k: int,
        course_id: Optional[str] = None,
        chat_memory: Optional[ChatMemory] = None
    ) -> QueryResponse:
        """基于检索的查询"""
        try:
            # 生成问题的嵌入向量
            question_embedding = Settings.embed_model.get_text_embedding(question)

            # 构建过滤条件
            filter_conditions = {}
            if course_id:
                filter_conditions["course_id"] = course_id

            # 执行向量搜索
            search_results = await self.qdrant_repo.search_points(
                collection_name=collection_name,
                query_vector=question_embedding,
                limit=top_k,
                filter_conditions=filter_conditions if filter_conditions else None
            )

            # 构建上下文
            context_parts = []
            sources = []

            for result in search_results:
                payload = result["payload"]
                context_parts.append(payload["text"])

                sources.append(SourceInfo(
                    course_id=payload["course_id"],
                    course_material_id=payload["course_material_id"],
                    course_material_name=payload["course_material_name"],
                    chunk_text=payload["text"][:200] + "..." if len(payload["text"]) > 200 else payload["text"],
                    score=result["score"]
                ))

            context_str = "\n\n".join(context_parts)

            # 使用RAG系统提示词生成回答
            prompt = self.rag_system_prompt.format(
                context_str=context_str,
                query_str=question
            )

            # 生成回答
            response = Settings.llm.complete(prompt)
            answer = response.text

            # 更新聊天记忆
            updated_memory = self._update_chat_memory(chat_memory, question, answer)

            return QueryResponse(
                answer=answer,
                sources=sources,
                chat_memory=updated_memory,
                mode=ChatMode.QUERY,
                processing_time=0  # 将在上层设置
            )

        except Exception as e:
            logger.error(f"检索查询失败: {e}")
            raise

    async def _query_direct_chat(
        self,
        question: str,
        chat_memory: Optional[ChatMemory] = None
    ) -> QueryResponse:
        """直接聊天查询"""
        try:
            # 创建简单聊天引擎
            chat_engine = SimpleChatEngine.from_defaults(llm=Settings.llm)

            # 如果有聊天记忆，构建对话历史
            if chat_memory and chat_memory.messages:
                # 这里可以根据需要实现更复杂的记忆管理
                pass

            # 生成回答
            response = chat_engine.chat(question)
            answer = str(response)

            # 更新聊天记忆
            updated_memory = self._update_chat_memory(chat_memory, question, answer)

            return QueryResponse(
                answer=answer,
                sources=[],  # 直接聊天模式没有来源
                chat_memory=updated_memory,
                mode=ChatMode.CHAT,
                processing_time=0  # 将在上层设置
            )

        except Exception as e:
            logger.error(f"直接聊天失败: {e}")
            raise

    def _update_chat_memory(
        self,
        chat_memory: Optional[ChatMemory],
        question: str,
        answer: str
    ) -> ChatMemory:
        """更新聊天记忆"""
        if chat_memory is None:
            chat_memory = ChatMemory()

        # 添加新的消息
        chat_memory.messages.append(ChatMessage(role="user", content=question))
        chat_memory.messages.append(ChatMessage(role="assistant", content=answer))

        # 简单的token计数（实际应该使用tokenizer）
        total_text = " ".join([msg.content for msg in chat_memory.messages])
        chat_memory.token_count = len(total_text.split())

        # 如果消息太多，可以在这里实现摘要逻辑
        if len(chat_memory.messages) > 20:  # 超过20条消息时进行摘要
            chat_memory = self._summarize_chat_memory(chat_memory)

        return chat_memory

    def _summarize_chat_memory(self, chat_memory: ChatMemory) -> ChatMemory:
        """摘要聊天记忆"""
        try:
            # 构建聊天历史文本
            chat_history = "\n".join([
                f"{msg.role}: {msg.content}" for msg in chat_memory.messages[:-4]  # 保留最后4条消息
            ])

            # 生成摘要
            prompt = self.chat_summary_prompt.format(chat_history=chat_history)
            response = Settings.llm.complete(prompt)
            summary = response.text

            # 创建新的记忆，保留摘要和最近的消息
            new_memory = ChatMemory(
                messages=chat_memory.messages[-4:],  # 保留最后4条消息
                summary=summary,
                token_count=len(summary.split()) + sum(len(msg.content.split()) for msg in chat_memory.messages[-4:])
            )

            return new_memory

        except Exception as e:
            logger.error(f"摘要聊天记忆失败: {e}")
            return chat_memory  # 失败时返回原记忆
