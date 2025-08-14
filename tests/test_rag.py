"""
RAG模块测试
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from app.core.config import Settings
from app.services.rag_service import RAGService
from app.repositories.rag_repository import QdrantRepository
from app.schemas.rag import (
    IndexRequest, QueryRequest, DocumentMetadata, 
    ChatMode, ChatMemory, ChatMessage
)


@pytest.fixture
def mock_settings():
    """模拟配置"""
    settings = Mock(spec=Settings)
    settings.api_key = "test-api-key"
    settings.base_url = "https://api.openai.com/v1"
    settings.rag_embed_model = "text-embedding-3-small"
    settings.rag_llm_model = "gpt-4o-mini"
    settings.qdrant_url = "http://localhost:6333"
    settings.qdrant_grpc_port = 6334
    settings.qdrant_prefer_grpc = True
    settings.qdrant_collection_name = "test_collection"
    settings.rag_chunk_size = 512
    settings.rag_chunk_overlap = 50
    settings.rag_top_k = 5
    return settings


@pytest.fixture
def mock_qdrant_repo():
    """模拟Qdrant仓库"""
    repo = Mock(spec=QdrantRepository)
    repo.create_collection = AsyncMock(return_value=True)
    repo.upsert_points = AsyncMock(return_value=True)
    repo.search_points = AsyncMock(return_value=[])
    repo.get_collections = AsyncMock(return_value=[])
    repo.delete_collection = AsyncMock(return_value=True)
    repo.get_collection_info = AsyncMock(return_value=None)
    repo.count_points = AsyncMock(return_value=0)
    return repo


@pytest.fixture
def sample_document_metadata():
    """示例文档元数据"""
    return DocumentMetadata(
        course_id="course_001",
        course_material_id="material_001",
        course_material_name="Python基础教程",
        file_path="/test/python_basics.md",
        file_size=1024
    )


@pytest.fixture
def sample_index_request(sample_document_metadata):
    """示例索引请求"""
    return IndexRequest(
        file_content="# Python基础\n\nPython是一种编程语言...",
        metadata=sample_document_metadata,
        collection_name="test_collection"
    )


@pytest.fixture
def sample_query_request():
    """示例查询请求"""
    return QueryRequest(
        question="什么是Python？",
        mode=ChatMode.QUERY,
        course_id="course_001",
        chat_memory=None,
        collection_name="test_collection",
        top_k=5
    )


class TestQdrantRepository:
    """Qdrant仓库测试"""
    
    def test_init(self, mock_settings):
        """测试初始化"""
        with patch('app.repositories.rag_repository.QdrantClient'):
            repo = QdrantRepository(mock_settings)
            assert repo.settings == mock_settings
    
    @pytest.mark.asyncio
    async def test_create_collection(self, mock_settings):
        """测试创建集合"""
        with patch('app.repositories.rag_repository.QdrantClient') as mock_client:
            # 模拟客户端
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.get_collections.return_value = Mock(collections=[])
            mock_instance.create_collection = Mock()
            
            repo = QdrantRepository(mock_settings)
            result = await repo.create_collection("test_collection")
            
            assert result is True
            mock_instance.create_collection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_points(self, mock_settings):
        """测试搜索向量点"""
        with patch('app.repositories.rag_repository.QdrantClient') as mock_client:
            # 模拟搜索结果
            mock_point = Mock()
            mock_point.id = "test_id"
            mock_point.score = 0.95
            mock_point.payload = {"text": "test content"}
            
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.search.return_value = [mock_point]
            
            repo = QdrantRepository(mock_settings)
            results = await repo.search_points(
                collection_name="test_collection",
                query_vector=[0.1] * 1536,
                limit=5
            )
            
            assert len(results) == 1
            assert results[0]["id"] == "test_id"
            assert results[0]["score"] == 0.95
            assert results[0]["payload"]["text"] == "test content"


class TestRAGService:
    """RAG服务测试"""
    
    @patch('app.services.rag_service.Settings')
    @patch('app.services.rag_service.QdrantRepository')
    def test_init(self, mock_repo_class, mock_settings_class, mock_settings):
        """测试RAG服务初始化"""
        with patch.object(RAGService, '_load_prompts'):
            service = RAGService(mock_settings)
            assert service.settings == mock_settings
            mock_repo_class.assert_called_once_with(mock_settings)
    
    @pytest.mark.asyncio
    async def test_build_index_success(self, mock_settings, sample_index_request):
        """测试成功建立索引"""
        with patch('app.services.rag_service.Settings'), \
             patch('app.services.rag_service.QdrantRepository') as mock_repo_class, \
             patch.object(RAGService, '_load_prompts'), \
             patch('app.services.rag_service.Document'), \
             patch('app.services.rag_service.uuid') as mock_uuid:
            
            # 模拟仓库
            mock_repo = Mock()
            mock_repo.create_collection = AsyncMock(return_value=True)
            mock_repo.upsert_points = AsyncMock(return_value=True)
            mock_repo_class.return_value = mock_repo
            
            # 模拟文本分块器
            mock_node = Mock()
            mock_node.text = "test chunk"
            
            # 模拟UUID生成
            mock_uuid.uuid4.return_value = Mock()
            mock_uuid.uuid4.return_value.__str__ = Mock(return_value="test-uuid")
            
            service = RAGService(mock_settings)
            service.text_splitter = Mock()
            service.text_splitter.get_nodes_from_documents.return_value = [mock_node]
            
            # 模拟嵌入模型
            mock_embed_model = Mock()
            mock_embed_model.get_text_embedding.return_value = [0.1] * 1536
            service.settings.embed_model = mock_embed_model
            
            response = await service.build_index(sample_index_request)
            
            assert response.success is True
            assert response.chunk_count == 1
            assert response.collection_name == "test_collection"
    
    @pytest.mark.asyncio
    async def test_query_retrieval_mode(self, mock_settings, sample_query_request):
        """测试检索模式查询"""
        with patch('app.services.rag_service.Settings') as mock_settings_class, \
             patch('app.services.rag_service.QdrantRepository') as mock_repo_class, \
             patch.object(RAGService, '_load_prompts'):
            
            # 模拟LLM设置
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.text = "Python是一种编程语言"
            mock_llm.complete.return_value = mock_response
            mock_settings_class.llm = mock_llm
            
            # 模拟嵌入模型
            mock_embed_model = Mock()
            mock_embed_model.get_text_embedding.return_value = [0.1] * 1536
            mock_settings_class.embed_model = mock_embed_model
            
            # 模拟仓库搜索结果
            mock_repo = Mock()
            mock_repo.search_points = AsyncMock(return_value=[
                {
                    "id": "test_id",
                    "score": 0.95,
                    "payload": {
                        "text": "Python是一种编程语言",
                        "course_id": "course_001",
                        "course_material_id": "material_001",
                        "course_material_name": "Python基础教程"
                    }
                }
            ])
            mock_repo_class.return_value = mock_repo
            
            service = RAGService(mock_settings)
            service.rag_system_prompt = "基于以下内容回答问题：\n{context_str}\n\n问题：{query_str}"
            
            response = await service.query(sample_query_request)
            
            assert response.mode == ChatMode.QUERY
            assert len(response.sources) == 1
            assert response.sources[0].course_id == "course_001"
    
    @pytest.mark.asyncio
    async def test_query_chat_mode(self, mock_settings):
        """测试直接聊天模式查询"""
        chat_request = QueryRequest(
            question="你好",
            mode=ChatMode.CHAT,
            chat_memory=None
        )
        
        with patch('app.services.rag_service.Settings') as mock_settings_class, \
             patch('app.services.rag_service.QdrantRepository'), \
             patch.object(RAGService, '_load_prompts'), \
             patch('app.services.rag_service.SimpleChatEngine') as mock_chat_engine_class:
            
            # 模拟聊天引擎
            mock_chat_engine = Mock()
            mock_chat_engine.chat.return_value = "你好！我是AI助手。"
            mock_chat_engine_class.from_defaults.return_value = mock_chat_engine
            
            service = RAGService(mock_settings)
            response = await service.query(chat_request)
            
            assert response.mode == ChatMode.CHAT
            assert len(response.sources) == 0  # 直接聊天模式没有来源
            assert "你好！我是AI助手。" in response.answer
    
    def test_update_chat_memory(self, mock_settings):
        """测试更新聊天记忆"""
        with patch('app.services.rag_service.Settings'), \
             patch('app.services.rag_service.QdrantRepository'), \
             patch.object(RAGService, '_load_prompts'):
            
            service = RAGService(mock_settings)
            
            # 测试空记忆
            memory = service._update_chat_memory(None, "问题", "答案")
            assert len(memory.messages) == 2
            assert memory.messages[0].role == "user"
            assert memory.messages[0].content == "问题"
            assert memory.messages[1].role == "assistant"
            assert memory.messages[1].content == "答案"
            
            # 测试现有记忆
            existing_memory = ChatMemory(
                messages=[ChatMessage(role="user", content="之前的问题")]
            )
            updated_memory = service._update_chat_memory(existing_memory, "新问题", "新答案")
            assert len(updated_memory.messages) == 3


class TestRAGSchemas:
    """RAG数据模型测试"""
    
    def test_document_metadata(self):
        """测试文档元数据模型"""
        metadata = DocumentMetadata(
            course_id="course_001",
            course_material_id="material_001",
            course_material_name="Python基础教程"
        )
        assert metadata.course_id == "course_001"
        assert metadata.course_material_id == "material_001"
        assert metadata.course_material_name == "Python基础教程"
    
    def test_chat_mode_enum(self):
        """测试聊天模式枚举"""
        assert ChatMode.QUERY == "query"
        assert ChatMode.CHAT == "chat"
    
    def test_query_request_defaults(self):
        """测试查询请求默认值"""
        request = QueryRequest(question="测试问题")
        assert request.mode == ChatMode.QUERY
        assert request.course_id is None
        assert request.chat_memory is None
