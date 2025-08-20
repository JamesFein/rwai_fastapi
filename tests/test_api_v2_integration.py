"""
API v2 集成测试
验证新的RAG和对话API路由的功能
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from io import BytesIO

from app.api.v1.rag_v2 import router as rag_v2_router
from app.api.v1.conversation_v2 import router as conversation_v2_router
from app.schemas.rag import ChatEngineType


@pytest.fixture
def app():
    """创建测试应用"""
    app = FastAPI()
    app.include_router(rag_v2_router)
    app.include_router(conversation_v2_router)
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


class TestRAGV2API:
    """RAG v2 API测试"""
    
    @patch('app.services.rag.document_indexing_service.DocumentIndexingService.build_index')
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_build_index_success(self, mock_get_service, mock_build_index, client):
        """测试成功建立索引"""
        # Mock服务
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message = "索引建立成功"
        mock_response.document_count = 1
        mock_response.chunk_count = 3
        mock_response.processing_time = 1.5
        mock_response.collection_name = "test_collection"
        
        # 直接mock build_index方法
        mock_build_index.return_value = mock_response

        # Mock服务实例
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # 准备测试文件
        test_content = "这是一个测试文档内容。"
        test_file = BytesIO(test_content.encode('utf-8'))
        
        # 发送请求
        response = client.post(
            "/rag/v2/index",
            files={"file": ("test.md", test_file, "text/markdown")},
            data={
                "course_id": "test_course",
                "course_material_id": "test_material",
                "course_material_name": "Test Material"
            }
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "索引建立成功"
        assert data["document_count"] == 1
        assert data["chunk_count"] == 3
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_build_index_invalid_file_type(self, mock_get_service, client):
        """测试无效文件类型"""
        # 准备测试文件
        test_content = "这是一个测试文档内容。"
        test_file = BytesIO(test_content.encode('utf-8'))
        
        # 发送请求
        response = client.post(
            "/rag/v2/index",
            files={"file": ("test.pdf", test_file, "application/pdf")},
            data={
                "course_id": "test_course",
                "course_material_id": "test_material",
                "course_material_name": "Test Material"
            }
        )
        
        # 验证响应
        assert response.status_code == 400
        data = response.json()
        assert "只支持.md和.txt文件" in data["detail"]
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_get_collections(self, mock_get_service, client):
        """测试获取集合列表"""
        # Mock服务
        mock_service = MagicMock()
        mock_collections = [
            MagicMock(name="collection1", vectors_count=100),
            MagicMock(name="collection2", vectors_count=200)
        ]
        mock_service.get_collections.return_value = mock_collections
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.get("/rag/v2/collections")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_get_collection_info(self, mock_get_service, client):
        """测试获取集合信息"""
        # Mock服务
        mock_service = MagicMock()
        mock_collection_info = MagicMock(name="test_collection", vectors_count=150)
        mock_service.get_collection_info.return_value = mock_collection_info
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.get("/rag/v2/collections/test_collection")
        
        # 验证响应
        assert response.status_code == 200
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_get_collection_info_not_found(self, mock_get_service, client):
        """测试获取不存在的集合信息"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.get_collection_info.return_value = None
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.get("/rag/v2/collections/nonexistent")
        
        # 验证响应
        assert response.status_code == 404
        data = response.json()
        assert "不存在" in data["detail"]
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_delete_collection(self, mock_get_service, client):
        """测试删除集合"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.delete_collection.return_value = True
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.delete("/rag/v2/collections/test_collection")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_delete_documents_by_course(self, mock_get_service, client):
        """测试按课程删除文档"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.delete_documents_by_course.return_value = 5
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.delete("/rag/v2/documents/course/test_course")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 5
        assert data["course_id"] == "test_course"
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_delete_documents_by_material(self, mock_get_service, client):
        """测试按课程材料删除文档"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.delete_documents_by_material.return_value = 3
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.delete("/rag/v2/documents/material/test_course/test_material")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 3
        assert data["course_id"] == "test_course"
        assert data["course_material_id"] == "test_material"
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_count_documents(self, mock_get_service, client):
        """测试统计文档数量"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.count_documents.return_value = 42
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.get("/rag/v2/collections/test_collection/count")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["collection_name"] == "test_collection"
        assert data["document_count"] == 42
    
    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    def test_health_check(self, mock_get_service, client):
        """测试健康检查"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.get_service_status.return_value = {
            "service_name": "DocumentIndexingService",
            "status": "healthy"
        }
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.get("/rag/v2/health")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "v2"


class TestConversationV2API:
    """对话 v2 API测试"""
    
    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_intelligent_chat_simple_engine(self, mock_get_service, client):
        """测试简单聊天引擎"""
        # Mock服务
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.answer = "你好！我是AI助手。"
        mock_response.sources = []
        mock_response.conversation_id = "test_conv"
        mock_response.chat_engine_type = ChatEngineType.SIMPLE
        mock_response.filter_info = "无过滤条件，搜索全部文档"
        mock_response.processing_time = 0.5
        
        mock_service.chat = AsyncMock(return_value=mock_response)
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.post(
            "/conversation/v2/chat",
            json={
                "conversation_id": "test_conv",
                "question": "你好",
                "chat_engine_type": "simple"
            }
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "你好！我是AI助手。"
        assert data["conversation_id"] == "test_conv"
        assert data["chat_engine_type"] == "simple"
        assert len(data["sources"]) == 0
    
    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_intelligent_chat_condense_plus_context_engine(self, mock_get_service, client):
        """测试condense_plus_context聊天引擎"""
        # Mock服务
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.answer = "Python是一种编程语言。"
        mock_response.sources = [
            MagicMock(
                course_id="python_course",
                course_material_id="python_intro",
                course_material_name="Python介绍",
                chunk_text="Python是一种高级编程语言",
                score=0.95
            )
        ]
        mock_response.conversation_id = "test_conv"
        mock_response.chat_engine_type = ChatEngineType.CONDENSE_PLUS_CONTEXT
        mock_response.filter_info = "course_id = python_course"
        mock_response.processing_time = 1.2
        
        mock_service.chat = AsyncMock(return_value=mock_response)
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.post(
            "/conversation/v2/chat",
            json={
                "conversation_id": "test_conv",
                "question": "什么是Python？",
                "chat_engine_type": "condense_plus_context",
                "course_id": "python_course"
            }
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Python是一种编程语言。"
        assert data["conversation_id"] == "test_conv"
        assert data["chat_engine_type"] == "condense_plus_context"
        assert len(data["sources"]) == 1
    
    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_chat_empty_conversation_id(self, mock_get_service, client):
        """测试空的对话ID"""
        # 发送请求
        response = client.post(
            "/conversation/v2/chat",
            json={
                "conversation_id": "",
                "question": "你好",
                "chat_engine_type": "simple"
            }
        )
        
        # 验证响应
        assert response.status_code == 400
        data = response.json()
        assert "conversation_id 不能为空" in data["detail"]
    
    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_chat_empty_question(self, mock_get_service, client):
        """测试空的问题"""
        # 发送请求
        response = client.post(
            "/conversation/v2/chat",
            json={
                "conversation_id": "test_conv",
                "question": "",
                "chat_engine_type": "simple"
            }
        )
        
        # 验证响应
        assert response.status_code == 400
        data = response.json()
        assert "question 不能为空" in data["detail"]

    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_clear_conversation(self, mock_get_service, client):
        """测试清除对话"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.clear_conversation = AsyncMock(return_value=True)
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.delete("/conversation/v2/conversations/test_conv")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["conversation_id"] == "test_conv"
        assert data["version"] == "v2"

    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_clear_conversation_empty_id(self, mock_get_service, client):
        """测试清除空对话ID"""
        # 发送请求
        response = client.delete("/conversation/v2/conversations/")

        # 验证响应
        assert response.status_code == 404  # FastAPI会返回404对于空路径参数

    def test_get_available_engines(self, client):
        """测试获取可用引擎"""
        # 发送请求
        response = client.get("/conversation/v2/engines")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "v2"
        assert "engines" in data
        assert len(data["engines"]) == 2

        # 验证引擎信息
        engine_types = [engine["type"] for engine in data["engines"]]
        assert "condense_plus_context" in engine_types
        assert "simple" in engine_types

    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_conversation_health_check(self, mock_get_service, client):
        """测试对话服务健康检查"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.get_service_status.return_value = {
            "service_name": "ConversationService",
            "status": "healthy"
        }
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.get("/conversation/v2/health")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "v2"

    def test_get_conversation_status(self, client):
        """测试获取对话状态"""
        # 发送请求
        response = client.get("/conversation/v2/conversations/test_conv/status")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == "test_conv"
        assert data["status"] == "active"
        assert data["version"] == "v2"

    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_get_conversation_config(self, mock_get_service, client):
        """测试获取对话配置"""
        # Mock服务
        mock_service = MagicMock()
        mock_service.get_service_status.return_value = {
            "rag_config": {"llm_model": "gpt-4o-mini"},
            "components": {"memory_manager": "ConversationMemoryManager"},
            "supported_engines": ["condense_plus_context", "simple"]
        }
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.get("/conversation/v2/config")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "v2"
        assert "configuration" in data
        assert "components" in data
        assert "supported_engines" in data


class TestAPIV2Integration:
    """API v2 集成测试"""

    @patch('app.api.v1.rag_v2.get_document_indexing_service')
    @patch('app.api.v1.conversation_v2.get_conversation_service')
    def test_full_workflow_index_and_chat(self, mock_conv_service, mock_doc_service, client):
        """测试完整的索引建立和对话工作流程"""
        # Mock文档索引服务
        mock_doc_svc = MagicMock()
        mock_index_response = MagicMock()
        mock_index_response.success = True
        mock_index_response.message = "索引建立成功"
        mock_index_response.document_count = 1
        mock_index_response.chunk_count = 3
        mock_doc_svc.build_index = AsyncMock(return_value=mock_index_response)
        mock_doc_service.return_value = mock_doc_svc

        # Mock对话服务
        mock_conv_svc = MagicMock()
        mock_chat_response = MagicMock()
        mock_chat_response.answer = "根据文档内容，Python是一种编程语言。"
        mock_chat_response.sources = [MagicMock(course_id="test_course")]
        mock_chat_response.conversation_id = "test_conv"
        mock_chat_response.chat_engine_type = ChatEngineType.CONDENSE_PLUS_CONTEXT
        mock_conv_svc.chat = AsyncMock(return_value=mock_chat_response)
        mock_conv_service.return_value = mock_conv_svc

        # 1. 建立索引
        test_content = "Python是一种编程语言。"
        test_file = BytesIO(test_content.encode('utf-8'))

        index_response = client.post(
            "/rag/v2/index",
            files={"file": ("test.md", test_file, "text/markdown")},
            data={
                "course_id": "test_course",
                "course_material_id": "test_material",
                "course_material_name": "Test Material"
            }
        )

        assert index_response.status_code == 200
        index_data = index_response.json()
        assert index_data["success"] is True

        # 2. 进行对话
        chat_response = client.post(
            "/conversation/v2/chat",
            json={
                "conversation_id": "test_conv",
                "question": "什么是Python？",
                "chat_engine_type": "condense_plus_context",
                "course_id": "test_course"
            }
        )

        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        assert "Python" in chat_data["answer"]
        assert len(chat_data["sources"]) > 0

    def test_api_version_consistency(self, client):
        """测试API版本一致性"""
        # 测试RAG v2健康检查
        rag_health = client.get("/rag/v2/health")
        assert rag_health.status_code == 200
        rag_data = rag_health.json()
        assert rag_data["version"] == "v2"

        # 测试对话v2健康检查
        conv_health = client.get("/conversation/v2/health")
        assert conv_health.status_code == 200
        conv_data = conv_health.json()
        assert conv_data["version"] == "v2"

        # 测试引擎信息
        engines = client.get("/conversation/v2/engines")
        assert engines.status_code == 200
        engines_data = engines.json()
        assert engines_data["version"] == "v2"
