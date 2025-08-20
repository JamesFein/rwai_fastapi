"""
RAG服务集成测试
验证新的文档索引服务和对话服务的功能和协作
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from app.core.config import Settings as AppSettings
from app.services.rag.rag_settings import RAGConfigManager
from app.services.rag.document_indexing_service import DocumentIndexingService
from app.services.rag.conversation_service import ConversationService
from app.schemas.rag import (
    IndexRequest, DocumentMetadata, ChatRequest, ChatEngineType
)


class TestDocumentIndexingService:
    """文档索引服务测试"""
    
    @pytest.fixture
    def app_settings(self):
        """应用配置fixture"""
        return AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            qdrant_collection_name="test_collection"
        )
    
    @pytest.fixture
    def rag_config_manager(self, app_settings):
        """RAG配置管理器fixture"""
        manager = RAGConfigManager()
        with patch('app.services.rag.rag_settings.Settings'), \
             patch('app.services.rag.rag_settings.OpenAI'), \
             patch('app.services.rag.rag_settings.OpenAIEmbedding'), \
             patch('app.services.rag.rag_settings.SentenceSplitter'):
            manager.initialize(app_settings)
        return manager
    
    @pytest.fixture
    def document_indexing_service(self, app_settings, rag_config_manager):
        """文档索引服务fixture"""
        with patch('app.services.rag.document_indexing_service.QdrantRepository'):
            return DocumentIndexingService(app_settings, rag_config_manager)
    
    @pytest.mark.asyncio
    async def test_build_index_success(self, document_indexing_service):
        """测试成功建立索引"""
        # 准备测试数据
        metadata = DocumentMetadata(
            course_id="test_course",
            course_material_id="test_material",
            course_material_name="Test Material",
            file_path="test.md",
            file_size=1000,
            upload_time=datetime.now().isoformat()
        )
        
        request = IndexRequest(
            file_content="这是一个测试文档内容。",
            metadata=metadata,
            collection_name="test_collection"
        )
        
        # Mock依赖
        with patch.object(document_indexing_service.qdrant_repo, 'create_collection', return_value=True), \
             patch.object(document_indexing_service.qdrant_repo, 'upsert_points', return_value=True), \
             patch('app.services.rag.document_indexing_service.Settings') as mock_settings, \
             patch('app.services.rag.document_indexing_service.Document') as mock_document:
            
            # 配置mock
            mock_embed_model = MagicMock()
            mock_embed_model.get_text_embedding.return_value = [0.1] * 1536
            mock_settings.embed_model = mock_embed_model
            
            mock_text_splitter = MagicMock()
            mock_node = MagicMock()
            mock_node.text = "测试文本块"
            mock_text_splitter.get_nodes_from_documents.return_value = [mock_node]
            document_indexing_service.rag_config_manager.text_splitter = mock_text_splitter
            
            # 执行测试
            response = await document_indexing_service.build_index(request)
            
            # 验证结果
            assert response.success is True
            assert response.message == "索引建立成功"
            assert response.document_count == 1
            assert response.chunk_count == 1
            assert response.collection_name == "test_collection"
    
    def test_get_collections(self, document_indexing_service):
        """测试获取集合列表"""
        # Mock返回数据
        mock_collections = [
            MagicMock(name="collection1", vectors_count=100),
            MagicMock(name="collection2", vectors_count=200)
        ]

        with patch.object(document_indexing_service.qdrant_repo, 'get_collections', return_value=mock_collections):
            collections = document_indexing_service.get_collections()

            assert len(collections) == 2
    
    def test_delete_documents_by_course(self, document_indexing_service):
        """测试按课程删除文档"""
        with patch.object(document_indexing_service.qdrant_repo, 'delete_vectors_by_filter', return_value=5):
            deleted_count = document_indexing_service.delete_documents_by_course("test_course")

            assert deleted_count == 5


class TestConversationService:
    """对话服务测试"""
    
    @pytest.fixture
    def app_settings(self):
        """应用配置fixture"""
        return AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            qdrant_collection_name="test_collection"
        )
    
    @pytest.fixture
    def rag_config_manager(self, app_settings):
        """RAG配置管理器fixture"""
        manager = RAGConfigManager()
        with patch('app.services.rag.rag_settings.Settings'), \
             patch('app.services.rag.rag_settings.OpenAI'), \
             patch('app.services.rag.rag_settings.OpenAIEmbedding'), \
             patch('app.services.rag.rag_settings.SentenceSplitter'):
            manager.initialize(app_settings)
        return manager
    
    @pytest.fixture
    def conversation_service(self, app_settings, rag_config_manager):
        """对话服务fixture"""
        with patch('app.services.rag.conversation_service.QdrantClient'), \
             patch('app.services.rag.conversation_service.VectorStoreIndex'), \
             patch('builtins.open', create=True) as mock_open:
            
            # Mock文件读取
            mock_open.return_value.__enter__.return_value.read.return_value = "测试提示词"
            
            return ConversationService(app_settings, rag_config_manager)
    
    @pytest.mark.asyncio
    async def test_chat_simple_engine(self, conversation_service):
        """测试简单聊天引擎"""
        request = ChatRequest(
            conversation_id="test_conv",
            question="你好",
            chat_engine_type=ChatEngineType.SIMPLE
        )
        
        # Mock内存管理器和引擎工厂
        mock_memory = MagicMock()
        mock_engine = MagicMock()
        mock_response = MagicMock()
        mock_response.__str__ = lambda self: "你好！我是AI助手。"
        mock_engine.chat.return_value = mock_response
        
        with patch.object(conversation_service.memory_manager, 'create_memory', return_value=mock_memory), \
             patch.object(conversation_service.engine_factory, 'create_engine', return_value=mock_engine):
            
            response = await conversation_service.chat(request)
            
            assert response.answer == "你好！我是AI助手。"
            assert response.conversation_id == "test_conv"
            assert response.chat_engine_type == ChatEngineType.SIMPLE
            assert len(response.sources) == 0
    
    @pytest.mark.asyncio
    async def test_chat_condense_plus_context_engine(self, conversation_service):
        """测试condense_plus_context聊天引擎"""
        request = ChatRequest(
            conversation_id="test_conv",
            question="什么是Python？",
            chat_engine_type=ChatEngineType.CONDENSE_PLUS_CONTEXT,
            course_id="python_course"
        )
        
        # Mock内存管理器和引擎工厂
        mock_memory = MagicMock()
        mock_engine = MagicMock()
        mock_response = MagicMock()
        mock_response.__str__ = lambda self: "Python是一种编程语言。"
        
        # Mock source nodes
        mock_source_node = MagicMock()
        mock_source_node.node.metadata = {
            "course_id": "python_course",
            "course_material_id": "python_intro",
            "course_material_name": "Python介绍"
        }
        mock_source_node.node.get_content.return_value = "Python是一种高级编程语言"
        mock_source_node.score = 0.95
        mock_response.source_nodes = [mock_source_node]
        
        mock_engine.chat.return_value = mock_response
        
        with patch.object(conversation_service.memory_manager, 'create_memory', return_value=mock_memory), \
             patch.object(conversation_service.engine_factory, 'create_engine', return_value=mock_engine):
            
            response = await conversation_service.chat(request)
            
            assert response.answer == "Python是一种编程语言。"
            assert response.conversation_id == "test_conv"
            assert response.chat_engine_type == ChatEngineType.CONDENSE_PLUS_CONTEXT
            assert len(response.sources) == 1
            assert response.sources[0].course_id == "python_course"
            assert response.sources[0].score == 0.95
    
    @pytest.mark.asyncio
    async def test_clear_conversation(self, conversation_service):
        """测试清除对话"""
        with patch.object(conversation_service.memory_manager, 'clear_conversation', return_value=True):
            success = await conversation_service.clear_conversation("test_conv")
            
            assert success is True


class TestServicesIntegration:
    """服务集成测试"""
    
    @pytest.fixture
    def app_settings(self):
        """应用配置fixture"""
        return AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            qdrant_collection_name="test_collection"
        )
    
    @pytest.fixture
    def rag_config_manager(self, app_settings):
        """RAG配置管理器fixture"""
        manager = RAGConfigManager()
        with patch('app.services.rag.rag_settings.Settings'), \
             patch('app.services.rag.rag_settings.OpenAI'), \
             patch('app.services.rag.rag_settings.OpenAIEmbedding'), \
             patch('app.services.rag.rag_settings.SentenceSplitter'):
            manager.initialize(app_settings)
        return manager
    
    @pytest.mark.asyncio
    async def test_document_indexing_and_conversation_workflow(self, app_settings, rag_config_manager):
        """测试文档索引和对话的完整工作流程"""
        # 创建服务实例
        with patch('app.services.rag.document_indexing_service.QdrantRepository'), \
             patch('app.services.rag.conversation_service.QdrantClient'), \
             patch('app.services.rag.conversation_service.VectorStoreIndex'), \
             patch('builtins.open', create=True) as mock_open:
            
            mock_open.return_value.__enter__.return_value.read.return_value = "测试提示词"
            
            doc_service = DocumentIndexingService(app_settings, rag_config_manager)
            conv_service = ConversationService(app_settings, rag_config_manager)
            
            # 1. 建立文档索引
            metadata = DocumentMetadata(
                course_id="test_course",
                course_material_id="test_material",
                course_material_name="Test Material",
                file_path="test.md",
                file_size=1000
            )
            
            index_request = IndexRequest(
                file_content="Python是一种编程语言。",
                metadata=metadata,
                collection_name="test_collection"
            )
            
            with patch.object(doc_service.qdrant_repo, 'create_collection', return_value=True), \
                 patch.object(doc_service.qdrant_repo, 'upsert_points', return_value=True), \
                 patch('app.services.rag.document_indexing_service.Settings') as mock_settings:
                
                mock_embed_model = MagicMock()
                mock_embed_model.get_text_embedding.return_value = [0.1] * 1536
                mock_settings.embed_model = mock_embed_model
                
                mock_text_splitter = MagicMock()
                mock_node = MagicMock()
                mock_node.text = "Python是一种编程语言。"
                mock_text_splitter.get_nodes_from_documents.return_value = [mock_node]
                doc_service.rag_config_manager.text_splitter = mock_text_splitter
                
                index_response = await doc_service.build_index(index_request)
                assert index_response.success is True
            
            # 2. 进行对话查询
            chat_request = ChatRequest(
                conversation_id="test_conv",
                question="什么是Python？",
                chat_engine_type=ChatEngineType.CONDENSE_PLUS_CONTEXT,
                course_id="test_course"
            )
            
            mock_memory = MagicMock()
            mock_engine = MagicMock()
            mock_response = MagicMock()
            mock_response.__str__ = lambda self: "Python是一种编程语言。"
            mock_response.source_nodes = []
            mock_engine.chat.return_value = mock_response
            
            with patch.object(conv_service.memory_manager, 'create_memory', return_value=mock_memory), \
                 patch.object(conv_service.engine_factory, 'create_engine', return_value=mock_engine):
                
                chat_response = await conv_service.chat(chat_request)
                assert chat_response.answer == "Python是一种编程语言。"
                assert chat_response.conversation_id == "test_conv"
    
    def test_service_status_methods(self, app_settings, rag_config_manager):
        """测试服务状态方法"""
        with patch('app.services.rag.document_indexing_service.QdrantRepository'), \
             patch('app.services.rag.conversation_service.QdrantClient'), \
             patch('app.services.rag.conversation_service.VectorStoreIndex'), \
             patch('builtins.open', create=True) as mock_open:
            
            mock_open.return_value.__enter__.return_value.read.return_value = "测试提示词"
            
            doc_service = DocumentIndexingService(app_settings, rag_config_manager)
            conv_service = ConversationService(app_settings, rag_config_manager)
            
            # 测试文档索引服务状态
            doc_status = doc_service.get_service_status()
            assert doc_status["service_name"] == "DocumentIndexingService"
            assert doc_status["status"] == "healthy"
            
            # 测试对话服务状态
            conv_status = conv_service.get_service_status()
            assert conv_status["service_name"] == "ConversationService"
            assert conv_status["status"] == "healthy"
            assert "condense_plus_context" in conv_status["supported_engines"]
            assert "simple" in conv_status["supported_engines"]
