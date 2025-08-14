#!/usr/bin/env python3
"""
RAG索引构建脚本
用于批量处理文档并建立向量索引
"""
import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any
import time
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import get_settings
from app.services.rag_service import RAGService
from app.schemas.rag import IndexRequest, DocumentMetadata


class RAGIndexBuilder:
    """RAG索引构建器"""
    
    def __init__(self):
        """初始化构建器"""
        self.settings = get_settings()
        self.rag_service = RAGService(self.settings)
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "start_time": None,
            "end_time": None
        }
    
    async def build_index_from_directory(
        self, 
        directory: Path, 
        course_id: str,
        collection_name: str = None,
        file_pattern: str = "*.md"
    ) -> Dict[str, Any]:
        """从目录批量构建索引"""
        self.stats["start_time"] = time.time()
        
        logger.info(f"开始处理目录: {directory}")
        logger.info(f"课程ID: {course_id}")
        logger.info(f"文件模式: {file_pattern}")
        logger.info(f"集合名称: {collection_name or self.settings.qdrant_collection_name}")
        
        # 查找所有匹配的文件
        files = list(directory.glob(file_pattern))
        if not files:
            logger.warning(f"在目录 {directory} 中未找到匹配 {file_pattern} 的文件")
            return self.stats
        
        self.stats["total_files"] = len(files)
        logger.info(f"找到 {len(files)} 个文件待处理")
        
        # 处理每个文件
        for i, file_path in enumerate(files, 1):
            logger.info(f"处理文件 {i}/{len(files)}: {file_path.name}")
            
            try:
                await self._process_file(file_path, course_id, collection_name)
                self.stats["processed_files"] += 1
                logger.info(f"✅ 文件处理成功: {file_path.name}")
            except Exception as e:
                self.stats["failed_files"] += 1
                logger.error(f"❌ 文件处理失败: {file_path.name} - {e}")
        
        self.stats["end_time"] = time.time()
        self._print_summary()
        
        return self.stats
    
    async def _process_file(
        self, 
        file_path: Path, 
        course_id: str,
        collection_name: str = None
    ):
        """处理单个文件"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 生成材料ID（基于文件名）
            material_id = f"material_{file_path.stem}"
            
            # 构建元数据
            metadata = DocumentMetadata(
                course_id=course_id,
                course_material_id=material_id,
                course_material_name=file_path.stem,
                file_path=str(file_path),
                file_size=len(content.encode('utf-8'))
            )
            
            # 构建索引请求
            request = IndexRequest(
                file_content=content,
                metadata=metadata,
                collection_name=collection_name
            )
            
            # 执行索引建立
            response = await self.rag_service.build_index(request)
            
            if response.success:
                self.stats["total_chunks"] += response.chunk_count
                logger.debug(f"文件 {file_path.name} 生成了 {response.chunk_count} 个文本块")
            else:
                raise Exception(response.message)
        
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {e}")
            raise
    
    def _print_summary(self):
        """打印处理摘要"""
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        logger.info("=" * 60)
        logger.info("📊 索引构建摘要")
        logger.info("=" * 60)
        logger.info(f"总文件数: {self.stats['total_files']}")
        logger.info(f"成功处理: {self.stats['processed_files']}")
        logger.info(f"处理失败: {self.stats['failed_files']}")
        logger.info(f"总文本块: {self.stats['total_chunks']}")
        logger.info(f"处理时间: {duration:.2f} 秒")
        
        if self.stats["processed_files"] > 0:
            avg_time = duration / self.stats["processed_files"]
            logger.info(f"平均处理时间: {avg_time:.2f} 秒/文件")
        
        success_rate = (self.stats["processed_files"] / self.stats["total_files"]) * 100
        logger.info(f"成功率: {success_rate:.1f}%")
        logger.info("=" * 60)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RAG索引构建脚本")
    parser.add_argument(
        "directory", 
        type=str, 
        help="包含文档的目录路径"
    )
    parser.add_argument(
        "--course-id", 
        type=str, 
        required=True,
        help="课程ID"
    )
    parser.add_argument(
        "--collection-name", 
        type=str, 
        help="Qdrant集合名称（可选，默认使用配置中的名称）"
    )
    parser.add_argument(
        "--pattern", 
        type=str, 
        default="*.md",
        help="文件匹配模式（默认: *.md）"
    )
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
    
    # 验证目录
    directory = Path(args.directory)
    if not directory.exists():
        logger.error(f"目录不存在: {directory}")
        sys.exit(1)
    
    if not directory.is_dir():
        logger.error(f"路径不是目录: {directory}")
        sys.exit(1)
    
    # 创建构建器并执行
    builder = RAGIndexBuilder()
    
    try:
        stats = await builder.build_index_from_directory(
            directory=directory,
            course_id=args.course_id,
            collection_name=args.collection_name,
            file_pattern=args.pattern
        )
        
        # 根据结果设置退出码
        if stats["failed_files"] == 0:
            logger.info("🎉 所有文件处理成功！")
            sys.exit(0)
        elif stats["processed_files"] > 0:
            logger.warning("⚠️ 部分文件处理失败")
            sys.exit(1)
        else:
            logger.error("❌ 所有文件处理失败")
            sys.exit(2)
    
    except Exception as e:
        logger.error(f"索引构建过程中出现错误: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
