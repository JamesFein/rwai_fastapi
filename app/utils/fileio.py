"""
文件输入输出工具模块
提供安全的文件操作功能
"""
import os
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple
import aiofiles
import aiofiles.os
from fastapi import HTTPException

from ..core.logging import get_logger
from ..constants.paths import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, CHUNK_SIZE

logger = get_logger("fileio")


class FileIOUtils:
    """文件IO工具类"""
    
    @staticmethod
    def is_safe_path(file_path: Path, base_path: Path) -> bool:
        """
        检查文件路径是否安全，防止目录遍历攻击
        
        Args:
            file_path: 要检查的文件路径
            base_path: 基础路径
            
        Returns:
            是否安全
        """
        try:
            # 解析绝对路径
            abs_file_path = file_path.resolve()
            abs_base_path = base_path.resolve()
            
            # 检查文件路径是否在基础路径内
            return abs_base_path in abs_file_path.parents or abs_base_path == abs_file_path
        except Exception:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 100) -> str:
        """
        清理文件名，移除不安全字符
        
        Args:
            filename: 原始文件名
            max_length: 最大长度
            
        Returns:
            清理后的文件名
        """
        # 移除路径分隔符和其他危险字符
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
        clean_name = filename
        
        for char in dangerous_chars:
            clean_name = clean_name.replace(char, '_')
        
        # 移除开头的点号（隐藏文件）
        clean_name = clean_name.lstrip('.')
        
        # 限制长度
        if len(clean_name) > max_length:
            name_part = Path(clean_name).stem[:max_length-10]
            ext_part = Path(clean_name).suffix
            clean_name = f"{name_part}{ext_part}"
        
        return clean_name or "unnamed_file"
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str] = None) -> bool:
        """
        验证文件扩展名
        
        Args:
            filename: 文件名
            allowed_extensions: 允许的扩展名列表
            
        Returns:
            是否有效
        """
        if allowed_extensions is None:
            allowed_extensions = ALLOWED_EXTENSIONS
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in allowed_extensions
    
    @staticmethod
    async def get_file_size(file_path: Path) -> int:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小（字节）
        """
        try:
            stat = await aiofiles.os.stat(file_path)
            return stat.st_size
        except Exception as e:
            logger.error(f"获取文件大小失败: {file_path}, 错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"无法获取文件大小: {str(e)}")
    
    @staticmethod
    async def calculate_file_hash(file_path: Path, algorithm: str = "md5") -> str:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法
            
        Returns:
            文件哈希值
        """
        try:
            hash_obj = hashlib.new(algorithm)
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(CHUNK_SIZE):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"计算文件哈希失败: {file_path}, 错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"计算文件哈希失败: {str(e)}")
    
    @staticmethod
    async def read_text_file_safe(
        file_path: Path,
        max_size: int = MAX_FILE_SIZE,
        encoding: str = "utf-8"
    ) -> str:
        """
        安全读取文本文件
        
        Args:
            file_path: 文件路径
            max_size: 最大文件大小
            encoding: 文件编码
            
        Returns:
            文件内容
        """
        try:
            # 检查文件是否存在
            if not await aiofiles.os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="文件不存在")
            
            # 检查文件大小
            file_size = await FileIOUtils.get_file_size(file_path)
            if file_size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"文件过大: {file_size} > {max_size} 字节"
                )
            
            # 读取文件内容
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                content = await f.read()
            
            logger.info(f"文件读取成功: {file_path}, 大小: {file_size} 字节")
            return content
            
        except UnicodeDecodeError:
            # 尝试其他编码
            for alt_encoding in ['gbk', 'gb2312', 'latin-1']:
                try:
                    async with aiofiles.open(file_path, 'r', encoding=alt_encoding) as f:
                        content = await f.read()
                    logger.info(f"使用 {alt_encoding} 编码读取文件成功: {file_path}")
                    return content
                except UnicodeDecodeError:
                    continue
            
            raise HTTPException(status_code=400, detail="无法解码文件，请检查文件编码")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"文件读取失败: {file_path}, 错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件读取失败: {str(e)}")
    
    @staticmethod
    async def write_text_file_safe(
        file_path: Path,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> None:
        """
        安全写入文本文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码
            create_dirs: 是否创建目录
        """
        try:
            # 创建目录
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
                await f.write(content)
            
            logger.info(f"文件写入成功: {file_path}, 长度: {len(content)} 字符")
            
        except Exception as e:
            logger.error(f"文件写入失败: {file_path}, 错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件写入失败: {str(e)}")
    
    @staticmethod
    async def copy_file_safe(
        source_path: Path,
        dest_path: Path,
        create_dirs: bool = True
    ) -> None:
        """
        安全复制文件
        
        Args:
            source_path: 源文件路径
            dest_path: 目标文件路径
            create_dirs: 是否创建目录
        """
        try:
            # 创建目标目录
            if create_dirs:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            async with aiofiles.open(source_path, 'rb') as src:
                async with aiofiles.open(dest_path, 'wb') as dst:
                    while chunk := await src.read(CHUNK_SIZE):
                        await dst.write(chunk)
            
            logger.info(f"文件复制成功: {source_path} -> {dest_path}")
            
        except Exception as e:
            logger.error(f"文件复制失败: {source_path} -> {dest_path}, 错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件复制失败: {str(e)}")
    
    @staticmethod
    async def delete_file_safe(file_path: Path) -> bool:
        """
        安全删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        try:
            if await aiofiles.os.path.exists(file_path):
                await aiofiles.os.remove(file_path)
                logger.info(f"文件删除成功: {file_path}")
                return True
            else:
                logger.warning(f"文件不存在，无需删除: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"文件删除失败: {file_path}, 错误: {str(e)}")
            return False


# 全局工具实例
file_utils = FileIOUtils()
