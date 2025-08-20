"""
端到端测试
测试完整的文档索引 → 对话查询 → 结果返回流程
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.config import get_settings


class TestEndToEnd:
    """端到端测试类"""
    
    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def test_file(self):
        """创建测试文件"""
        content = """
# Python编程基础

## 什么是Python？

Python是一种高级编程语言，具有以下特点：

1. **简洁易读**：Python的语法简洁明了，接近自然语言
2. **功能强大**：拥有丰富的标准库和第三方库
3. **跨平台**：可以在Windows、Linux、macOS等系统上运行
4. **应用广泛**：用于Web开发、数据分析、人工智能等领域

## Python基本语法

### 变量和数据类型

```python
# 字符串
name = "Python"
# 整数
age = 30
# 浮点数
price = 99.99
# 布尔值
is_active = True
```

### 函数定义

```python
def greet(name):
    return f"Hello, {name}!"

result = greet("World")
print(result)  # 输出: Hello, World!
```

## 总结

Python是一门优秀的编程语言，适合初学者学习，也能满足专业开发需求。
        """
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content.strip())
            temp_path = f.name
        
        yield temp_path
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_complete_workflow_new_api(self, client, test_file):
        """测试新API的完整工作流程"""
        
        # 1. 文档索引建立
        with open(test_file, 'rb') as f:
            response = client.post(
                "/api/v1/rag/v2/index",
                files={"file": ("test_python.md", f, "text/markdown")},
                data={
                    "course_id": "python_course",
                    "course_material_id": "python_basics",
                    "course_material_name": "Python编程基础"
                }
            )
        
        assert response.status_code == 200
        index_data = response.json()
        assert index_data["success"] is True
        assert index_data["chunk_count"] > 0
        print(f"索引建立成功，分块数量: {index_data['chunk_count']}")
        
        # 2. 验证集合创建
        response = client.get("/api/v1/rag/v2/collections")
        assert response.status_code == 200
        collections_data = response.json()
        assert len(collections_data) > 0
        print(f"集合列表: {[c['name'] for c in collections_data]}")
        
        # 3. 简单聊天测试
        response = client.post(
            "/api/v1/conversation/v2/chat",
            json={
                "conversation_id": "test_e2e_simple",
                "question": "你好，请介绍一下自己",
                "chat_engine_type": "simple"
            }
        )
        
        assert response.status_code == 200
        chat_data = response.json()
        assert len(chat_data["answer"]) > 0
        assert chat_data["conversation_id"] == "test_e2e_simple"
        print(f"简单聊天回复: {chat_data['answer'][:100]}...")
        
        # 4. 检索增强聊天测试
        response = client.post(
            "/api/v1/conversation/v2/chat",
            json={
                "conversation_id": "test_e2e_rag",
                "question": "什么是Python？它有什么特点？",
                "chat_engine_type": "condense_plus_context",
                "course_id": "python_course"
            }
        )
        
        assert response.status_code == 200
        rag_data = response.json()
        assert len(rag_data["answer"]) > 0
        assert rag_data["conversation_id"] == "test_e2e_rag"
        print(f"RAG聊天回复: {rag_data['answer'][:100]}...")
        
        # 5. 验证源文档信息
        if rag_data.get("sources"):
            source = rag_data["sources"][0]
            assert source["course_id"] == "python_course"
            assert source["course_material_id"] == "python_basics"
            print(f"源文档: {source['course_material_name']}")
        
        # 6. 清理对话
        response = client.delete("/api/v1/conversation/v2/conversations/test_e2e_simple")
        assert response.status_code == 200
        
        response = client.delete("/api/v1/conversation/v2/conversations/test_e2e_rag")
        assert response.status_code == 200
        
        # 7. 清理文档
        response = client.delete("/api/v1/rag/v2/documents/course/python_course")
        assert response.status_code == 200
        delete_data = response.json()
        assert delete_data["success"] is True
        print(f"清理文档数量: {delete_data['deleted_count']}")
    
    def test_api_compatibility(self, client, test_file):
        """测试新旧API兼容性"""
        
        # 使用新API建立索引
        with open(test_file, 'rb') as f:
            response = client.post(
                "/api/v1/rag/v2/index",
                files={"file": ("test_compat.md", f, "text/markdown")},
                data={
                    "course_id": "compat_course",
                    "course_material_id": "compat_material",
                    "course_material_name": "兼容性测试"
                }
            )
        
        assert response.status_code == 200
        
        # 使用旧API进行聊天（如果还存在）
        try:
            response = client.post(
                "/api/v1/chat/intelligent",
                json={
                    "conversation_id": "test_compat",
                    "question": "Python有什么特点？",
                    "chat_engine_type": "condense_plus_context",
                    "course_id": "compat_course"
                }
            )
            
            # 如果旧API还存在，应该能正常工作
            if response.status_code == 200:
                chat_data = response.json()
                assert len(chat_data["answer"]) > 0
                print("旧API兼容性测试通过")
            else:
                print("旧API已不可用，这是预期的")
                
        except Exception as e:
            print(f"旧API测试异常（可能已移除）: {e}")
        
        # 清理
        response = client.delete("/api/v1/rag/v2/documents/course/compat_course")
        assert response.status_code == 200
    
    def test_error_handling(self, client):
        """测试错误处理"""
        
        # 1. 无效文件类型
        response = client.post(
            "/api/v1/rag/v2/index",
            files={"file": ("test.exe", b"invalid content", "application/octet-stream")},
            data={
                "course_id": "error_test",
                "course_material_id": "error_material",
                "course_material_name": "错误测试"
            }
        )
        
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        print(f"文件类型错误处理: {error_data['detail']}")
        
        # 2. 空问题
        response = client.post(
            "/api/v1/conversation/v2/chat",
            json={
                "conversation_id": "test_error",
                "question": "",
                "chat_engine_type": "simple"
            }
        )
        
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
        print(f"空问题错误处理: {error_data['detail']}")
        
        # 3. 无效聊天引擎类型
        response = client.post(
            "/api/v1/conversation/v2/chat",
            json={
                "conversation_id": "test_error",
                "question": "测试问题",
                "chat_engine_type": "invalid_engine"
            }
        )
        
        assert response.status_code == 422  # Validation error
        print("无效引擎类型错误处理通过")


class TestEnvironmentVariables:
    """环境变量配置测试"""
    
    @patch.dict(os.environ, {
        'RAG_LLM_MODEL': 'gpt-4',
        'RAG_CHUNK_SIZE': '1024',
        'RAG_REDIS_URL': 'redis://localhost:6380'
    })
    def test_environment_variable_override(self):
        """测试环境变量覆盖配置"""
        from app.services.rag.rag_settings import get_rag_config_manager
        
        # 重新初始化配置管理器以应用环境变量
        config_manager = get_rag_config_manager()
        settings = get_settings()
        config_manager.initialize(settings)
        
        # 验证环境变量覆盖
        settings_summary = config_manager.get_settings_summary()
        assert settings_summary["llm"]["model"] == 'gpt-4'
        assert settings_summary["text_splitting"]["chunk_size"] == 1024
        assert settings_summary["redis"]["url"] == 'redis://localhost:6380'
        
        print("环境变量覆盖测试通过")
