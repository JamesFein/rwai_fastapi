"""
依赖注入模块
定义 FastAPI 应用的公共依赖项
"""
from fastapi import Depends, HTTPException, UploadFile
from typing import Generator, Optional
import aiofiles
from pathlib import Path
import uuid
from datetime import datetime

from .config import Settings, get_settings
from .logging import get_logger

logger = get_logger("deps")


def get_current_settings() -> Settings:
    """获取当前配置 - 依赖注入用"""
    return get_settings()


async def validate_upload_file(
    file: UploadFile,
    settings: Settings = Depends(get_current_settings)
) -> UploadFile:
    """验证上传的文件"""
    
    # 检查文件是否存在
    if not file:
        raise HTTPException(status_code=400, detail="未提供文件")
    
    # 检查文件名
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(settings.allowed_extensions)}"
        )
    
    # 检查文件大小
    if hasattr(file, 'size') and file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制: {file.size} > {settings.max_file_size} 字节"
        )
    
    logger.info(f"文件验证通过: {file.filename}, 大小: {getattr(file, 'size', 'unknown')}")
    return file


def generate_task_id() -> str:
    """生成任务ID"""
    return str(uuid.uuid4())


def generate_filename(original_filename: str, task_id: str = None) -> str:
    """生成安全的文件名"""
    if not task_id:
        task_id = generate_task_id()
    
    # 获取文件扩展名
    file_ext = Path(original_filename).suffix
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 组合文件名: timestamp_taskid_original.ext
    safe_original = Path(original_filename).stem[:50]  # 限制原文件名长度
    new_filename = f"{timestamp}_{task_id[:8]}_{safe_original}{file_ext}"
    
    return new_filename


async def save_upload_file(
    file: UploadFile,
    save_path: Path,
    chunk_size: int = 8192
) -> int:
    """保存上传的文件"""
    total_size = 0
    
    try:
        async with aiofiles.open(save_path, 'wb') as f:
            while chunk := await file.read(chunk_size):
                await f.write(chunk)
                total_size += len(chunk)
        
        logger.info(f"文件保存成功: {save_path}, 大小: {total_size} 字节")
        return total_size
        
    except Exception as e:
        logger.error(f"文件保存失败: {save_path}, 错误: {str(e)}")
        # 清理可能的部分文件
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")


async def read_text_file(file_path: Path, encoding: str = "utf-8") -> str:
    """读取文本文件内容"""
    try:
        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            content = await f.read()
        
        logger.info(f"文件读取成功: {file_path}, 长度: {len(content)} 字符")
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
        
    except Exception as e:
        logger.error(f"文件读取失败: {file_path}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件读取失败: {str(e)}")


async def write_text_file(file_path: Path, content: str, encoding: str = "utf-8") -> None:
    """写入文本文件"""
    try:
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
            await f.write(content)
        
        logger.info(f"文件写入成功: {file_path}, 长度: {len(content)} 字符")
        
    except Exception as e:
        logger.error(f"文件写入失败: {file_path}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件写入失败: {str(e)}")
