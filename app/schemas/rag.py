"""
RAG模块数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ChatMode(str, Enum):
    """聊天模式枚举"""
    QUERY = "query"  # 检索模式（condense_question ChatEngine）
    CHAT = "chat"    # 直接聊天模式（simple ChatEngine）


class DocumentMetadata(BaseModel):
    """文档元数据模型"""
    course_id: str = Field(..., description="课程ID")
    course_material_id: str = Field(..., description="课程材料ID")
    course_material_name: str = Field(..., description="课程材料名称")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_size: Optional[int] = Field(None, description="文件大小")
    upload_time: Optional[str] = Field(None, description="上传时间")


class IndexRequest(BaseModel):
    """索引建立请求模型"""
    file_content: str = Field(..., description="文件内容")
    metadata: DocumentMetadata = Field(..., description="文档元数据")
    collection_name: Optional[str] = Field(None, description="集合名称，默认使用配置中的名称")


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="角色：user/assistant")
    content: str = Field(..., description="消息内容")


class ChatMemory(BaseModel):
    """聊天记忆模型"""
    messages: List[ChatMessage] = Field(default_factory=list, description="聊天消息列表")
    summary: Optional[str] = Field(None, description="对话摘要")
    token_count: int = Field(default=0, description="Token数量")


class QueryRequest(BaseModel):
    """问答查询请求模型"""
    question: str = Field(..., description="用户问题")
    mode: ChatMode = Field(default=ChatMode.QUERY, description="聊天模式")
    course_id: Optional[str] = Field(None, description="课程ID，用于过滤检索范围")
    chat_memory: Optional[ChatMemory] = Field(None, description="聊天记忆")
    collection_name: Optional[str] = Field(None, description="集合名称，默认使用配置中的名称")
    top_k: Optional[int] = Field(None, description="检索Top-K数量，默认使用配置中的值")


class SourceInfo(BaseModel):
    """来源信息模型"""
    course_id: str = Field(..., description="课程ID")
    course_material_id: str = Field(..., description="课程材料ID")
    course_material_name: str = Field(..., description="课程材料名称")
    chunk_text: str = Field(..., description="相关文本片段")
    score: float = Field(..., description="相似度分数")


class QueryResponse(BaseModel):
    """问答响应模型"""
    answer: str = Field(..., description="回答内容")
    sources: List[SourceInfo] = Field(default_factory=list, description="来源信息列表")
    chat_memory: Optional[ChatMemory] = Field(None, description="更新后的聊天记忆")
    mode: ChatMode = Field(..., description="使用的聊天模式")
    processing_time: float = Field(..., description="处理时间（秒）")


class IndexResponse(BaseModel):
    """索引建立响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    document_count: int = Field(default=0, description="处理的文档数量")
    chunk_count: int = Field(default=0, description="生成的文本块数量")
    processing_time: float = Field(..., description="处理时间（秒）")
    collection_name: str = Field(..., description="集合名称")


class CollectionInfo(BaseModel):
    """集合信息模型"""
    name: str = Field(..., description="集合名称")
    vectors_count: int = Field(..., description="向量数量")
    indexed_only: bool = Field(..., description="是否仅索引")
    payload_schema: Dict[str, Any] = Field(default_factory=dict, description="载荷模式")


class CollectionListResponse(BaseModel):
    """集合列表响应模型"""
    collections: List[CollectionInfo] = Field(..., description="集合列表")
    total_count: int = Field(..., description="总数量")


class DeleteCollectionResponse(BaseModel):
    """删除集合响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    collection_name: str = Field(..., description="被删除的集合名称")
