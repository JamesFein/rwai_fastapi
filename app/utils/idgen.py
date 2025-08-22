"""
ID生成工具模块
提供各种ID和文件名生成功能
"""
import uuid
import time
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.logging import get_logger

logger = get_logger("idgen")


class IDGenerator:
    """ID生成器类"""
    
    @staticmethod
    def generate_uuid() -> str:
        """生成UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """
        生成短ID
        
        Args:
            length: ID长度
            
        Returns:
            短ID字符串
        """
        characters = string.ascii_lowercase + string.digits
        return ''.join(random.choices(characters, k=length))
    
    @staticmethod
    def generate_timestamp_id() -> str:
        """生成基于时间戳的ID"""
        timestamp = int(time.time() * 1000)  # 毫秒时间戳
        random_suffix = IDGenerator.generate_short_id(4)
        return f"{timestamp}_{random_suffix}"
    
    @staticmethod
    def generate_task_id() -> str:
        """生成任务ID"""
        return IDGenerator.generate_uuid()
    
    @staticmethod
    def generate_session_id() -> str:
        """生成会话ID"""
        return IDGenerator.generate_timestamp_id()


class FilenameGenerator:
    """文件名生成器类"""
    
    @staticmethod
    def generate_timestamp_filename(
        original_filename: str,
        task_id: Optional[str] = None,
        prefix: str = "",
        suffix: str = ""
    ) -> str:
        """
        生成带时间戳的文件名
        
        Args:
            original_filename: 原始文件名
            task_id: 任务ID
            prefix: 前缀
            suffix: 后缀
            
        Returns:
            新文件名
        """
        # 获取文件扩展名
        file_path = Path(original_filename)
        file_ext = file_path.suffix
        file_stem = file_path.stem
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成任务ID部分
        if task_id:
            task_part = task_id[:8]  # 取前8位
        else:
            task_part = IDGenerator.generate_short_id(8)
        
        # 清理原始文件名
        clean_stem = FilenameGenerator._sanitize_filename_part(file_stem, max_length=30)
        
        # 组合文件名部分
        parts = []
        if prefix:
            parts.append(prefix)
        parts.extend([timestamp, task_part, clean_stem])
        if suffix:
            parts.append(suffix)
        
        # 组合最终文件名
        new_filename = "_".join(parts) + file_ext
        
        logger.debug(f"生成文件名: {original_filename} -> {new_filename}")
        return new_filename
    
    @staticmethod
    def generate_output_filename(
        original_filename: str,
        output_type: str,
        task_id: Optional[str] = None
    ) -> str:
        """
        生成输出文件名
        
        Args:
            original_filename: 原始文件名
            output_type: 输出类型 (outline, summary, etc.)
            task_id: 任务ID
            
        Returns:
            输出文件名
        """
        return FilenameGenerator.generate_timestamp_filename(
            original_filename=original_filename,
            task_id=task_id,
            prefix=output_type
        )
    
    @staticmethod
    def generate_upload_filename(
        original_filename: str,
        task_id: Optional[str] = None
    ) -> str:
        """
        生成上传文件名
        
        Args:
            original_filename: 原始文件名
            task_id: 任务ID
            
        Returns:
            上传文件名
        """
        return FilenameGenerator.generate_timestamp_filename(
            original_filename=original_filename,
            task_id=task_id,
            prefix="upload"
        )
    
    @staticmethod
    def _sanitize_filename_part(filename_part: str, max_length: int = 50) -> str:
        """
        清理文件名部分
        
        Args:
            filename_part: 文件名部分
            max_length: 最大长度
            
        Returns:
            清理后的文件名部分
        """
        # 移除危险字符
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0', ' ']
        clean_part = filename_part
        
        for char in dangerous_chars:
            clean_part = clean_part.replace(char, '_')
        
        # 移除连续的下划线
        while '__' in clean_part:
            clean_part = clean_part.replace('__', '_')
        
        # 移除开头和结尾的下划线
        clean_part = clean_part.strip('_')
        
        # 限制长度
        if len(clean_part) > max_length:
            clean_part = clean_part[:max_length]
        
        return clean_part or "unnamed"


class PathGenerator:
    """路径生成器类"""

    @staticmethod
    def generate_upload_path(
        base_dir: Path,
        filename: str,
        create_subdirs: bool = True
    ) -> Path:
        """
        生成上传文件路径（旧版本，保持兼容性）

        Args:
            base_dir: 基础目录
            filename: 文件名
            create_subdirs: 是否创建子目录

        Returns:
            文件路径
        """
        if create_subdirs:
            # 按日期创建子目录
            date_subdir = datetime.now().strftime("%Y/%m/%d")
            file_path = base_dir / date_subdir / filename
        else:
            file_path = base_dir / filename

        return file_path

    @staticmethod
    def generate_course_upload_path(
        base_dir: Path,
        course_id: str,
        course_material_id: str,
        material_name: str,
        file_extension: str
    ) -> Path:
        """
        生成基于课程的上传文件路径

        Args:
            base_dir: 基础目录 (data/uploads)
            course_id: 课程ID
            course_material_id: 课程材料ID
            material_name: 材料名称 (保留参数以兼容现有调用，但不再使用)
            file_extension: 文件扩展名 (包含点号，如 .md)

        Returns:
            文件路径: data/uploads/course_{course_id}/course_material_{course_material_id}{extension}
        """
        # 生成文件名: course_material_{course_material_id}{extension}
        filename = f"course_material_{course_material_id}{file_extension}"

        # 生成路径: base_dir/course_{course_id}/filename
        file_path = base_dir / f"course_{course_id}" / filename

        logger.debug(f"生成课程上传路径: {file_path}")
        return file_path

    @staticmethod
    def generate_course_outline_path(
        base_dir: Path,
        course_id: str,
        course_material_id: str,
        material_name: str
    ) -> Path:
        """
        生成基于课程的大纲输出文件路径

        Args:
            base_dir: 基础目录 (data/outputs/outlines)
            course_id: 课程ID
            course_material_id: 课程材料ID
            material_name: 材料名称 (保留参数以兼容现有调用，但不再使用)

        Returns:
            文件路径: data/outputs/outlines/course_{course_id}/course_material_{course_material_id}.md
        """
        # 生成文件名: course_material_{course_material_id}.md
        filename = f"course_material_{course_material_id}.md"

        # 生成路径: base_dir/course_{course_id}/filename
        file_path = base_dir / f"course_{course_id}" / filename

        logger.debug(f"生成课程大纲路径: {file_path}")
        return file_path
    
    @staticmethod
    def generate_output_path(
        base_dir: Path,
        filename: str,
        output_type: str,
        create_subdirs: bool = True
    ) -> Path:
        """
        生成输出文件路径
        
        Args:
            base_dir: 基础目录
            filename: 文件名
            output_type: 输出类型
            create_subdirs: 是否创建子目录
            
        Returns:
            文件路径
        """
        if create_subdirs:
            # 按类型和日期创建子目录
            date_subdir = datetime.now().strftime("%Y/%m/%d")
            file_path = base_dir / output_type / date_subdir / filename
        else:
            file_path = base_dir / output_type / filename
        
        return file_path


# 全局生成器实例
id_generator = IDGenerator()
filename_generator = FilenameGenerator()
path_generator = PathGenerator()
