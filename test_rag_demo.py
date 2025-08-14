#!/usr/bin/env python3
"""
RAG模块演示脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import get_settings
from app.services.rag_service import RAGService
from app.schemas.rag import IndexRequest, QueryRequest, DocumentMetadata, ChatMode


async def test_rag_functionality():
    """测试RAG功能"""
    print("🚀 开始测试RAG功能...")
    
    # 获取配置
    settings = get_settings()
    print(f"📋 使用配置:")
    print(f"  - API Key: {settings.api_key[:10]}...")
    print(f"  - Base URL: {settings.base_url}")
    print(f"  - Qdrant URL: {settings.qdrant_url}")
    print(f"  - 集合名称: {settings.qdrant_collection_name}")
    
    # 创建RAG服务
    try:
        rag_service = RAGService(settings)
        print("✅ RAG服务初始化成功")
    except Exception as e:
        print(f"❌ RAG服务初始化失败: {e}")
        return False
    
    # 测试文档内容
    test_content = """# Python 函数基础

## 什么是函数？

函数是带名字的代码块，用于完成具体的工作。要执行函数定义的特定任务，可调用该函数。

## 定义函数

使用关键字 def 来定义函数：

```python
def greet_user():
    print("Hello!")

greet_user()
```

## 向函数传递信息

可以在函数定义的括号内添加参数：

```python
def greet_user(username):
    print(f"Hello, {username.title()}!")

greet_user('alice')
```

## 实参和形参

- **形参**：函数定义中的变量
- **实参**：调用函数时传递给函数的信息
"""
    
    # 1. 测试索引建立
    print("\n📚 测试索引建立...")
    try:
        metadata = DocumentMetadata(
            course_id="python_course_001",
            course_material_id="lesson_functions",
            course_material_name="Python函数基础"
        )
        
        index_request = IndexRequest(
            file_content=test_content,
            metadata=metadata
        )
        
        index_response = await rag_service.build_index(index_request)
        
        if index_response.success:
            print(f"✅ 索引建立成功!")
            print(f"  - 文档数量: {index_response.document_count}")
            print(f"  - 文本块数量: {index_response.chunk_count}")
            print(f"  - 处理时间: {index_response.processing_time:.2f}秒")
        else:
            print(f"❌ 索引建立失败: {index_response.message}")
            return False
    except Exception as e:
        print(f"❌ 索引建立异常: {e}")
        return False
    
    # 2. 测试检索模式查询
    print("\n🔍 测试检索模式查询...")
    try:
        query_request = QueryRequest(
            question="什么是Python函数？",
            mode=ChatMode.QUERY,
            course_id="python_course_001"
        )
        
        query_response = await rag_service.query(query_request)
        
        print(f"📝 问题: {query_request.question}")
        print(f"💬 回答: {query_response.answer}")
        print(f"📊 来源数量: {len(query_response.sources)}")
        print(f"⏱️ 处理时间: {query_response.processing_time:.2f}秒")
        
        if query_response.sources:
            print("📖 相关来源:")
            for i, source in enumerate(query_response.sources[:2], 1):
                print(f"  {i}. {source.course_material_name} (相似度: {source.score:.3f})")
                print(f"     内容片段: {source.chunk_text[:100]}...")
    except Exception as e:
        print(f"❌ 检索查询异常: {e}")
        return False
    
    # 3. 测试直接聊天模式
    print("\n💬 测试直接聊天模式...")
    try:
        chat_request = QueryRequest(
            question="你好，请介绍一下自己",
            mode=ChatMode.CHAT
        )
        
        chat_response = await rag_service.query(chat_request)
        
        print(f"📝 问题: {chat_request.question}")
        print(f"💬 回答: {chat_response.answer}")
        print(f"📊 来源数量: {len(chat_response.sources)} (应该为0)")
        print(f"⏱️ 处理时间: {chat_response.processing_time:.2f}秒")
    except Exception as e:
        print(f"❌ 聊天查询异常: {e}")
        return False
    
    # 4. 测试集合管理
    print("\n📋 测试集合管理...")
    try:
        collections = await rag_service.qdrant_repo.get_collections()
        print(f"📊 当前集合数量: {len(collections)}")
        
        for collection in collections:
            print(f"  - {collection.name}: {collection.vectors_count} 个向量")
    except Exception as e:
        print(f"❌ 集合管理异常: {e}")
        return False
    
    print("\n🎉 RAG功能测试完成！")
    return True


async def main():
    """主函数"""
    try:
        success = await test_rag_functionality()
        if success:
            print("\n✅ 所有测试通过！RAG模块工作正常。")
            return 0
        else:
            print("\n❌ 测试失败！请检查配置和服务状态。")
            return 1
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
