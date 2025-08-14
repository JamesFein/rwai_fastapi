"""
应用配置管理模块
使用 pydantic-settings 进行类型安全的配置管理
"""
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用配置类"""
    
    # OpenAI API 配置
    api_key: str = Field(..., description="OpenAI API密钥")
    base_url: str = Field(default="https://api.openai.com/v1", description="OpenAI API基础URL")
    outline_model: str = Field(default="gpt-4o-mini", description="大纲生成模型")
    refine_model: str = Field(default="gpt-4o-mini", description="大纲精简模型")
    
    # RAG 配置
    rag_embed_model: str = Field(default="text-embedding-3-small", description="RAG嵌入模型")
    rag_llm_model: str = Field(default="gpt-4o-mini", description="RAG语言模型")
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant向量数据库URL")
    qdrant_grpc_port: int = Field(default=6334, description="Qdrant gRPC端口")
    qdrant_prefer_grpc: bool = Field(default=True, description="优先使用gRPC连接")
    qdrant_collection_name: str = Field(default="course_materials", description="Qdrant集合名称")
    rag_chunk_size: int = Field(default=512, description="RAG文本分块大小")
    rag_chunk_overlap: int = Field(default=50, description="RAG文本分块重叠")
    rag_top_k: int = Field(default=5, description="RAG检索Top-K数量")
    
    # GraphRAG 配置 (为后续模块预留)
    graph_rag_workdir: str = Field(default="./data/outputs/graphrag", description="GraphRAG工作目录")
    
    # 服务配置
    host: str = Field(default="0.0.0.0", description="服务监听地址")
    port: int = Field(default=8000, description="服务端口")
    debug: bool = Field(default=False, description="调试模式")
    
    # 文件配置
    max_file_size: int = Field(default=10485760, description="最大文件大小(字节)")  # 10MB
    allowed_extensions: List[str] = Field(default=[".md", ".txt"], description="允许的文件扩展名")
    
    # 路径配置
    upload_dir: str = Field(default="./data/uploads", description="上传目录")
    output_dir: str = Field(default="./data/outputs", description="输出目录")
    outline_output_dir: str = Field(default="./data/outputs/outlines", description="大纲输出目录")
    temp_dir: str = Field(default="./data/tmp", description="临时目录")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    
    # API配置
    api_v1_prefix: str = Field(default="/api/v1", description="API v1前缀")
    
    @validator("allowed_extensions")
    def validate_extensions(cls, v):
        """验证文件扩展名格式"""
        if isinstance(v, str):
            v = [ext.strip() for ext in v.split(",")]
        return [ext if ext.startswith(".") else f".{ext}" for ext in v]
    
    @validator("max_file_size")
    def validate_file_size(cls, v):
        """验证文件大小限制"""
        if v <= 0:
            raise ValueError("文件大小限制必须大于0")
        return v
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        dirs = [
            self.upload_dir,
            self.output_dir,
            self.outline_output_dir,
            self.temp_dir,
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例 - 用于依赖注入"""
    return settings
