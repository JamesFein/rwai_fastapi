"""
RAG配置管理器单元测试
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from app.services.rag.rag_settings import RAGConfigManager, RAGSettings, initialize_rag_config
from app.core.config import Settings as AppSettings


class TestRAGSettings:
    """RAG设置类测试"""
    
    def test_default_values(self):
        """测试默认配置值"""
        settings = RAGSettings()
        
        assert settings.redis_url == "redis://localhost:6379"
        assert settings.redis_ttl == 3600
        assert settings.conversation_token_limit == 4000
        assert settings.conversation_similarity_top_k == 6
        assert settings.llm_model == "gpt-4o-mini"
        assert settings.llm_temperature == 0.1
        assert settings.embed_model == "text-embedding-3-small"
        assert settings.chunk_size == 512
        assert settings.chunk_overlap == 50
        assert settings.qdrant_host == "localhost"
        assert settings.qdrant_port == 6334
        assert settings.qdrant_prefer_grpc is True
        assert settings.qdrant_timeout == 10
    
    def test_environment_variable_override(self):
        """测试环境变量覆盖配置"""
        with patch.dict(os.environ, {
            'RAG_REDIS_URL': 'redis://test:6379',
            'RAG_REDIS_TTL': '7200',
            'RAG_LLM_MODEL': 'gpt-4',
            'RAG_CHUNK_SIZE': '1024'
        }):
            settings = RAGSettings()
            
            assert settings.redis_url == "redis://test:6379"
            assert settings.redis_ttl == 7200
            assert settings.llm_model == "gpt-4"
            assert settings.chunk_size == 1024


class TestRAGConfigManager:
    """RAG配置管理器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 重置单例状态
        RAGConfigManager._instance = None
        RAGConfigManager._initialized = False
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        manager1 = RAGConfigManager()
        manager2 = RAGConfigManager()
        
        assert manager1 is manager2
    
    @patch('app.services.rag.rag_settings.Settings')
    @patch('app.services.rag.rag_settings.OpenAI')
    @patch('app.services.rag.rag_settings.OpenAIEmbedding')
    @patch('app.services.rag.rag_settings.SentenceSplitter')
    def test_initialize_success(self, mock_splitter, mock_embedding, mock_llm, mock_settings):
        """测试成功初始化"""
        # 准备测试数据
        app_settings = AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1"
        )
        
        # 创建管理器并初始化
        manager = RAGConfigManager()
        manager.initialize(app_settings)
        
        # 验证初始化状态
        assert manager.app_settings is app_settings
        assert manager.rag_settings is not None
        assert manager.text_splitter is not None
        
        # 验证LlamaIndex配置被调用
        mock_llm.assert_called_once()
        mock_embedding.assert_called_once()
        mock_splitter.assert_called_once()
    
    def test_initialize_without_app_settings(self):
        """测试未提供应用设置时的初始化"""
        manager = RAGConfigManager()
        
        with pytest.raises(Exception):
            manager.initialize(None)
    
    @patch('app.services.rag.rag_settings.Settings')
    @patch('app.services.rag.rag_settings.OpenAI')
    @patch('app.services.rag.rag_settings.OpenAIEmbedding')
    @patch('app.services.rag.rag_settings.SentenceSplitter')
    def test_get_config_methods(self, mock_splitter, mock_embedding, mock_llm, mock_settings):
        """测试配置获取方法"""
        app_settings = AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1"
        )
        
        manager = RAGConfigManager()
        manager.initialize(app_settings)
        
        # 测试Redis配置
        redis_config = manager.get_redis_config()
        assert "redis_url" in redis_config
        assert "ttl" in redis_config
        
        # 测试Qdrant配置
        qdrant_config = manager.get_qdrant_config()
        assert "host" in qdrant_config
        assert "port" in qdrant_config
        assert "prefer_grpc" in qdrant_config
        assert "timeout" in qdrant_config
        
        # 测试对话配置
        conversation_config = manager.get_conversation_config()
        assert "token_limit" in conversation_config
        assert "similarity_top_k" in conversation_config
    
    @patch('app.services.rag.rag_settings.Settings')
    @patch('app.services.rag.rag_settings.OpenAI')
    @patch('app.services.rag.rag_settings.OpenAIEmbedding')
    @patch('app.services.rag.rag_settings.SentenceSplitter')
    def test_get_text_splitter(self, mock_splitter, mock_embedding, mock_llm, mock_settings):
        """测试文本分块器获取"""
        app_settings = AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1"
        )
        
        manager = RAGConfigManager()
        manager.initialize(app_settings)
        
        # 测试获取文本分块器
        splitter = manager.get_text_splitter()
        assert splitter is not None
    
    def test_get_text_splitter_not_initialized(self):
        """测试未初始化时获取文本分块器"""
        manager = RAGConfigManager()
        
        with pytest.raises(RuntimeError, match="文本分块器未初始化"):
            manager.get_text_splitter()
    
    @patch('app.services.rag.rag_settings.Settings')
    @patch('app.services.rag.rag_settings.OpenAI')
    @patch('app.services.rag.rag_settings.OpenAIEmbedding')
    @patch('app.services.rag.rag_settings.SentenceSplitter')
    def test_reload_settings(self, mock_splitter, mock_embedding, mock_llm, mock_settings):
        """测试配置重新加载"""
        app_settings = AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1"
        )
        
        manager = RAGConfigManager()
        manager.initialize(app_settings)
        
        # 重新加载配置
        manager.reload_settings()
        
        # 验证配置被重新创建
        assert manager.rag_settings is not None
        assert manager.text_splitter is not None
    
    @patch('app.services.rag.rag_settings.Settings')
    @patch('app.services.rag.rag_settings.OpenAI')
    @patch('app.services.rag.rag_settings.OpenAIEmbedding')
    @patch('app.services.rag.rag_settings.SentenceSplitter')
    def test_get_settings_summary(self, mock_splitter, mock_embedding, mock_llm, mock_settings):
        """测试配置摘要获取"""
        app_settings = AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1"
        )
        
        manager = RAGConfigManager()
        manager.initialize(app_settings)
        
        # 获取配置摘要
        summary = manager.get_settings_summary()
        
        # 验证摘要结构
        assert "redis" in summary
        assert "llm" in summary
        assert "embedding" in summary
        assert "text_splitting" in summary
        assert "qdrant" in summary
        assert "conversation" in summary
    
    def test_get_settings_summary_not_initialized(self):
        """测试未初始化时获取配置摘要"""
        manager = RAGConfigManager()
        
        summary = manager.get_settings_summary()
        assert "error" in summary
        assert summary["error"] == "配置未初始化"


class TestModuleFunctions:
    """模块级函数测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 重置单例状态
        RAGConfigManager._instance = None
        RAGConfigManager._initialized = False
    
    @patch('app.services.rag.rag_settings.rag_config_manager')
    def test_initialize_rag_config(self, mock_manager):
        """测试RAG配置初始化函数"""
        app_settings = AppSettings(
            api_key="test-key",
            base_url="https://api.test.com/v1"
        )
        
        initialize_rag_config(app_settings)
        
        # 验证管理器的initialize方法被调用
        mock_manager.initialize.assert_called_once_with(app_settings)
