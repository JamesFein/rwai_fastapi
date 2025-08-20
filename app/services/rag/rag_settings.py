"""
RAG配置管理器
统一管理LlamaIndex全局配置，支持环境变量覆盖默认配置
"""
import os
from typing import Optional
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings

# LlamaIndex imports
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter

from app.core.config import Settings as AppSettings


class RAGSettings(BaseSettings):
    """RAG专用配置类，支持环境变量覆盖"""
    
    # Redis 配置
    redis_url: str = Field(default="redis://localhost:6379", description="Redis连接URL")
    redis_ttl: int = Field(default=3600, description="Redis数据TTL（秒）")
    
    # 对话配置
    conversation_token_limit: int = Field(default=4000, description="对话内存Token限制")
    conversation_similarity_top_k: int = Field(default=6, description="对话检索Top-K")
    
    # LLM 配置
    llm_model: str = Field(default="gpt-4o-mini", description="LLM模型名称")
    llm_temperature: float = Field(default=0.1, description="LLM温度参数")
    
    # 嵌入模型配置
    embed_model: str = Field(default="text-embedding-3-small", description="嵌入模型名称")
    
    # 文本分块配置
    chunk_size: int = Field(default=512, description="文本分块大小")
    chunk_overlap: int = Field(default=50, description="文本分块重叠")
    
    # Qdrant 配置
    qdrant_host: str = Field(default="localhost", description="Qdrant主机地址")
    qdrant_port: int = Field(default=6334, description="Qdrant gRPC端口")
    qdrant_prefer_grpc: bool = Field(default=True, description="优先使用gRPC连接")
    qdrant_timeout: int = Field(default=10, description="Qdrant连接超时（秒）")
    
    class Config:
        env_prefix = "RAG_"  # 环境变量前缀
        case_sensitive = False


class RAGConfigManager:
    """RAG配置管理器 - 单例模式"""
    
    _instance: Optional['RAGConfigManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'RAGConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.app_settings: Optional[AppSettings] = None
            self.rag_settings: Optional[RAGSettings] = None
            self.text_splitter: Optional[SentenceSplitter] = None
            self._initialized = True
    
    def initialize(self, app_settings: AppSettings) -> None:
        """
        初始化RAG配置管理器
        
        Args:
            app_settings: 应用配置实例
        """
        try:
            self.app_settings = app_settings
            self.rag_settings = RAGSettings()
            
            # 设置LlamaIndex全局配置
            self._setup_llama_index()
            
            # 初始化文本分块器
            self._setup_text_splitter()
            
            logger.info("RAG配置管理器初始化完成")
            logger.info(f"Redis URL: {self.rag_settings.redis_url}")
            logger.info(f"LLM模型: {self.rag_settings.llm_model}")
            logger.info(f"嵌入模型: {self.rag_settings.embed_model}")
            
        except Exception as e:
            logger.error(f"RAG配置管理器初始化失败: {e}")
            raise
    
    def _setup_llama_index(self) -> None:
        """设置LlamaIndex全局配置"""
        try:
            # 配置LLM
            Settings.llm = OpenAI(
                model=self.rag_settings.llm_model,
                api_key=self.app_settings.api_key,
                api_base=self.app_settings.base_url,
                temperature=self.rag_settings.llm_temperature
            )
            
            # 配置嵌入模型
            Settings.embed_model = OpenAIEmbedding(
                model=self.rag_settings.embed_model,
                api_key=self.app_settings.api_key,
                api_base=self.app_settings.base_url
            )
            
            logger.info("LlamaIndex全局配置完成")
            
        except Exception as e:
            logger.error(f"LlamaIndex配置失败: {e}")
            raise
    
    def _setup_text_splitter(self) -> None:
        """设置文本分块器"""
        try:
            self.text_splitter = SentenceSplitter(
                chunk_size=self.rag_settings.chunk_size,
                chunk_overlap=self.rag_settings.chunk_overlap
            )
            
            logger.info(f"文本分块器配置完成 - 块大小: {self.rag_settings.chunk_size}, 重叠: {self.rag_settings.chunk_overlap}")
            
        except Exception as e:
            logger.error(f"文本分块器配置失败: {e}")
            raise
    
    def get_redis_config(self) -> dict:
        """获取Redis配置"""
        return {
            "redis_url": self.rag_settings.redis_url,
            "ttl": self.rag_settings.redis_ttl
        }
    
    def get_qdrant_config(self) -> dict:
        """获取Qdrant配置"""
        return {
            "host": self.rag_settings.qdrant_host,
            "port": self.rag_settings.qdrant_port,
            "prefer_grpc": self.rag_settings.qdrant_prefer_grpc,
            "timeout": self.rag_settings.qdrant_timeout
        }
    
    def get_conversation_config(self) -> dict:
        """获取对话配置"""
        return {
            "token_limit": self.rag_settings.conversation_token_limit,
            "similarity_top_k": self.rag_settings.conversation_similarity_top_k
        }
    
    def get_text_splitter(self) -> SentenceSplitter:
        """获取文本分块器实例"""
        if self.text_splitter is None:
            raise RuntimeError("文本分块器未初始化，请先调用initialize()方法")
        return self.text_splitter
    
    def reload_settings(self) -> None:
        """重新加载配置（支持运行时配置更新）"""
        try:
            logger.info("重新加载RAG配置...")
            
            # 重新加载RAG设置
            self.rag_settings = RAGSettings()
            
            # 重新设置LlamaIndex配置
            self._setup_llama_index()
            
            # 重新设置文本分块器
            self._setup_text_splitter()
            
            logger.info("RAG配置重新加载完成")
            
        except Exception as e:
            logger.error(f"RAG配置重新加载失败: {e}")
            raise
    
    def get_settings_summary(self) -> dict:
        """获取配置摘要信息"""
        if not self.rag_settings:
            return {"error": "配置未初始化"}
        
        return {
            "redis": {
                "url": self.rag_settings.redis_url,
                "ttl": self.rag_settings.redis_ttl
            },
            "llm": {
                "model": self.rag_settings.llm_model,
                "temperature": self.rag_settings.llm_temperature
            },
            "embedding": {
                "model": self.rag_settings.embed_model
            },
            "text_splitting": {
                "chunk_size": self.rag_settings.chunk_size,
                "chunk_overlap": self.rag_settings.chunk_overlap
            },
            "qdrant": {
                "host": self.rag_settings.qdrant_host,
                "port": self.rag_settings.qdrant_port,
                "prefer_grpc": self.rag_settings.qdrant_prefer_grpc,
                "timeout": self.rag_settings.qdrant_timeout
            },
            "conversation": {
                "token_limit": self.rag_settings.conversation_token_limit,
                "similarity_top_k": self.rag_settings.conversation_similarity_top_k
            }
        }


# 全局RAG配置管理器实例
rag_config_manager = RAGConfigManager()


def get_rag_config_manager() -> RAGConfigManager:
    """获取RAG配置管理器实例"""
    return rag_config_manager


def initialize_rag_config(app_settings: AppSettings) -> None:
    """初始化RAG配置（应用启动时调用）"""
    rag_config_manager.initialize(app_settings)
