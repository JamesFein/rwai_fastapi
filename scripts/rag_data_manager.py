#!/usr/bin/env python3
"""
RAG数据管理脚本
用于管理Qdrant向量数据库中的数据
"""
import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import get_settings
from app.repositories.rag_repository import QdrantRepository


class RAGDataManager:
    """RAG数据管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.settings = get_settings()
        self.qdrant_repo = QdrantRepository(self.settings)
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """列出所有集合"""
        try:
            collections = await self.qdrant_repo.get_collections()
            
            logger.info("📋 集合列表:")
            logger.info("-" * 60)
            
            if not collections:
                logger.info("暂无集合")
                return []
            
            collection_data = []
            for collection in collections:
                data = {
                    "name": collection.name,
                    "vectors_count": collection.vectors_count,
                    "indexed_only": collection.indexed_only
                }
                collection_data.append(data)
                
                logger.info(f"集合名称: {collection.name}")
                logger.info(f"向量数量: {collection.vectors_count}")
                logger.info(f"仅索引: {collection.indexed_only}")
                logger.info("-" * 60)
            
            return collection_data
        
        except Exception as e:
            logger.error(f"获取集合列表失败: {e}")
            raise
    
    async def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        try:
            logger.info(f"准备删除集合: {collection_name}")
            
            # 确认删除
            confirm = input(f"确认删除集合 '{collection_name}' 吗？这将删除所有数据！(y/N): ")
            if confirm.lower() != 'y':
                logger.info("取消删除操作")
                return False
            
            success = await self.qdrant_repo.delete_collection(collection_name)
            
            if success:
                logger.info(f"✅ 集合 {collection_name} 删除成功")
            else:
                logger.error(f"❌ 集合 {collection_name} 删除失败")
            
            return success
        
        except Exception as e:
            logger.error(f"删除集合失败: {e}")
            raise
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """获取集合详细信息"""
        try:
            collection_info = await self.qdrant_repo.get_collection_info(collection_name)
            
            if not collection_info:
                logger.error(f"集合 {collection_name} 不存在")
                return {}
            
            logger.info(f"📊 集合 {collection_name} 详细信息:")
            logger.info("-" * 60)
            logger.info(f"名称: {collection_info.name}")
            logger.info(f"向量数量: {collection_info.vectors_count}")
            logger.info(f"仅索引: {collection_info.indexed_only}")
            
            if collection_info.payload_schema:
                logger.info("载荷模式:")
                for key, value in collection_info.payload_schema.items():
                    logger.info(f"  {key}: {value}")
            
            return {
                "name": collection_info.name,
                "vectors_count": collection_info.vectors_count,
                "indexed_only": collection_info.indexed_only,
                "payload_schema": collection_info.payload_schema
            }
        
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            raise
    
    async def backup_collection_info(self, output_file: str = None) -> str:
        """备份集合信息到JSON文件"""
        try:
            collections = await self.qdrant_repo.get_collections()
            
            backup_data = {
                "timestamp": str(asyncio.get_event_loop().time()),
                "collections": []
            }
            
            for collection in collections:
                collection_data = {
                    "name": collection.name,
                    "vectors_count": collection.vectors_count,
                    "indexed_only": collection.indexed_only,
                    "payload_schema": collection.payload_schema
                }
                backup_data["collections"].append(collection_data)
            
            # 生成输出文件名
            if not output_file:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"qdrant_backup_{timestamp}.json"
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 集合信息已备份到: {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"备份集合信息失败: {e}")
            raise
    
    async def create_collection(
        self, 
        collection_name: str, 
        vector_size: int = 1536
    ) -> bool:
        """创建新集合"""
        try:
            logger.info(f"创建集合: {collection_name}")
            logger.info(f"向量维度: {vector_size}")
            
            success = await self.qdrant_repo.create_collection(
                collection_name=collection_name,
                vector_size=vector_size
            )
            
            if success:
                logger.info(f"✅ 集合 {collection_name} 创建成功")
            else:
                logger.error(f"❌ 集合 {collection_name} 创建失败")
            
            return success
        
        except Exception as e:
            logger.error(f"创建集合失败: {e}")
            raise
    
    async def count_vectors(self, collection_name: str) -> int:
        """统计集合中的向量数量"""
        try:
            count = await self.qdrant_repo.count_points(collection_name)
            logger.info(f"集合 {collection_name} 包含 {count} 个向量")
            return count
        
        except Exception as e:
            logger.error(f"统计向量数量失败: {e}")
            raise
    
    def close(self):
        """关闭连接"""
        self.qdrant_repo.close()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RAG数据管理脚本")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 列出集合
    list_parser = subparsers.add_parser("list", help="列出所有集合")
    
    # 删除集合
    delete_parser = subparsers.add_parser("delete", help="删除集合")
    delete_parser.add_argument("collection_name", help="要删除的集合名称")
    
    # 获取集合信息
    info_parser = subparsers.add_parser("info", help="获取集合详细信息")
    info_parser.add_argument("collection_name", help="集合名称")
    
    # 备份集合信息
    backup_parser = subparsers.add_parser("backup", help="备份集合信息")
    backup_parser.add_argument("--output", help="输出文件路径")
    
    # 创建集合
    create_parser = subparsers.add_parser("create", help="创建新集合")
    create_parser.add_argument("collection_name", help="集合名称")
    create_parser.add_argument("--vector-size", type=int, default=1536, help="向量维度（默认: 1536）")
    
    # 统计向量数量
    count_parser = subparsers.add_parser("count", help="统计集合中的向量数量")
    count_parser.add_argument("collection_name", help="集合名称")
    
    # 日志级别
    parser.add_argument(
        "--log-level", 
        type=str, 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别（默认: INFO）"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 创建管理器
    manager = RAGDataManager()
    
    try:
        if args.command == "list":
            await manager.list_collections()
        
        elif args.command == "delete":
            success = await manager.delete_collection(args.collection_name)
            sys.exit(0 if success else 1)
        
        elif args.command == "info":
            info = await manager.get_collection_info(args.collection_name)
            sys.exit(0 if info else 1)
        
        elif args.command == "backup":
            output_file = await manager.backup_collection_info(args.output)
            logger.info(f"备份完成: {output_file}")
        
        elif args.command == "create":
            success = await manager.create_collection(
                args.collection_name, 
                args.vector_size
            )
            sys.exit(0 if success else 1)
        
        elif args.command == "count":
            count = await manager.count_vectors(args.collection_name)
            logger.info(f"向量数量: {count}")
    
    except Exception as e:
        logger.error(f"执行命令时出错: {e}")
        sys.exit(1)
    
    finally:
        manager.close()


if __name__ == "__main__":
    asyncio.run(main())
