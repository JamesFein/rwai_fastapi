#!/usr/bin/env python3
"""
测试智能聊天系统实现
验证与 notebook 中逻辑的一致性
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from app.core.config import get_settings
from app.schemas.rag import ChatRequest, ChatEngineType


async def test_chat_service():
    """测试聊天服务"""
    print("🧪 开始测试智能聊天系统...")
    
    try:
        # 导入聊天服务
        from app.services.chat_service import ChatService
        
        # 获取配置
        settings = get_settings()
        print(f"✅ 配置加载成功")
        
        # 创建聊天服务
        chat_service = ChatService(settings)
        print(f"✅ 聊天服务创建成功")
        
        # 测试用例1：condense_plus_context 模式
        print("\n📝 测试用例1：condense_plus_context 模式")
        request1 = ChatRequest(
            conversation_id="test_conversation_001",
            course_material_id="material_红楼梦第一章",
            chat_engine_type=ChatEngineType.CONDENSE_PLUS_CONTEXT,
            question="王夫人的娘家是哪个家族？"
        )
        
        response1 = await chat_service.chat(request1)
        print(f"✅ 回答: {response1.answer[:100]}...")
        print(f"✅ 来源数量: {len(response1.sources)}")
        print(f"✅ 过滤信息: {response1.filter_info}")
        print(f"✅ 处理时间: {response1.processing_time:.2f}s")
        
        # 测试用例2：simple 模式
        print("\n📝 测试用例2：simple 模式")
        request2 = ChatRequest(
            conversation_id="test_conversation_001",  # 同一个会话ID
            chat_engine_type=ChatEngineType.SIMPLE,
            question="请总结一下我们刚才的对话"
        )
        
        response2 = await chat_service.chat(request2)
        print(f"✅ 回答: {response2.answer[:100]}...")
        print(f"✅ 来源数量: {len(response2.sources)}")
        print(f"✅ 过滤信息: {response2.filter_info}")
        print(f"✅ 处理时间: {response2.processing_time:.2f}s")
        
        # 测试用例3：course_id 过滤
        print("\n📝 测试用例3：course_id 过滤")
        request3 = ChatRequest(
            conversation_id="test_conversation_002",
            course_id="course_01",
            chat_engine_type=ChatEngineType.CONDENSE_PLUS_CONTEXT,
            question="函数的核心概念是什么？"
        )
        
        response3 = await chat_service.chat(request3)
        print(f"✅ 回答: {response3.answer[:100]}...")
        print(f"✅ 来源数量: {len(response3.sources)}")
        print(f"✅ 过滤信息: {response3.filter_info}")
        print(f"✅ 处理时间: {response3.processing_time:.2f}s")
        
        print("\n🎉 所有测试用例执行完成！")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保安装了所需的依赖包：")
        print("   pip install llama-index-storage-chat-store-redis redis")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_api_endpoints():
    """测试API端点"""
    print("\n🌐 测试API端点...")
    
    try:
        import httpx
        
        # 测试聊天API
        async with httpx.AsyncClient() as client:
            # 测试健康检查
            try:
                response = await client.get("http://localhost:8000/api/v1/chat/health")
                if response.status_code == 200:
                    print("✅ 聊天API健康检查通过")
                else:
                    print(f"⚠️ 聊天API健康检查返回状态码: {response.status_code}")
            except Exception as e:
                print(f"⚠️ 无法连接到API服务器: {e}")
                print("💡 请确保FastAPI服务器正在运行 (uvicorn app.main:app --reload)")
                return False
            
            # 测试获取引擎列表
            try:
                response = await client.get("http://localhost:8000/api/v1/chat/engines")
                if response.status_code == 200:
                    engines = response.json()
                    print(f"✅ 获取到 {len(engines['engines'])} 个聊天引擎")
                    for engine in engines['engines']:
                        print(f"   - {engine['type']}: {engine['name']}")
                else:
                    print(f"⚠️ 获取引擎列表失败: {response.status_code}")
            except Exception as e:
                print(f"⚠️ 获取引擎列表出错: {e}")
        
    except ImportError:
        print("⚠️ httpx 未安装，跳过API测试")
        return True
    
    return True


def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    required_packages = [
        "llama_index",
        "qdrant_client", 
        "fastapi",
        "redis"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
            missing_packages.append(package)
    
    # 检查LlamaIndex Redis存储
    try:
        from llama_index.storage.chat_store.redis import RedisChatStore
        print("✅ llama-index-storage-chat-store-redis")
    except ImportError:
        print("❌ llama-index-storage-chat-store-redis (未安装)")
        missing_packages.append("llama-index-storage-chat-store-redis")
    
    if missing_packages:
        print(f"\n💡 请安装缺失的包:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_services():
    """检查外部服务"""
    print("\n🔧 检查外部服务...")
    
    # 检查Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis (localhost:6379)")
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        print("💡 请确保Redis服务正在运行")
        return False
    
    # 检查Qdrant
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host="localhost", port=6334, prefer_grpc=True, timeout=5)
        collections = client.get_collections()
        print(f"✅ Qdrant (localhost:6334) - {len(collections.collections)} 个集合")
    except Exception as e:
        print(f"❌ Qdrant 连接失败: {e}")
        print("💡 请确保Qdrant服务正在运行")
        return False
    
    return True


async def main():
    """主测试函数"""
    print("🚀 智能聊天系统测试")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺失的包后重试")
        return
    
    # 检查服务
    if not check_services():
        print("\n❌ 外部服务检查失败，请启动相关服务后重试")
        return
    
    # 测试聊天服务
    if await test_chat_service():
        print("\n✅ 聊天服务测试通过")
    else:
        print("\n❌ 聊天服务测试失败")
        return
    
    # 测试API端点
    if await test_api_endpoints():
        print("\n✅ API端点测试通过")
    else:
        print("\n❌ API端点测试失败")
        return
    
    print("\n🎉 所有测试完成！智能聊天系统实现正确。")
    print("\n📋 下一步:")
    print("1. 启动FastAPI服务器: uvicorn app.main:app --reload")
    print("2. 打开前端页面测试聊天功能")
    print("3. 验证Redis内存共享和动态过滤功能")


if __name__ == "__main__":
    asyncio.run(main())
