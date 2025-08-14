"""
文件和数据验证工具模块
提供各种验证功能
"""
import os
from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException

from ..core.logging import get_logger
from ..constants.paths import UPLOADS_DIR

logger = get_logger("validation")


class CourseValidation:
    """课程相关验证工具类"""
    
    @staticmethod
    def validate_course_material_id_unique(
        course_id: str,
        course_material_id: str,
        uploads_base_dir: Path = UPLOADS_DIR
    ) -> bool:
        """
        验证在指定course_id下course_material_id是否唯一
        
        Args:
            course_id: 课程ID
            course_material_id: 课程材料ID
            uploads_base_dir: 上传文件基础目录
            
        Returns:
            True if unique, False if exists
            
        Raises:
            HTTPException: 如果course_material_id已存在
        """
        try:
            # 构建课程目录路径
            course_dir = uploads_base_dir / course_id
            
            # 如果课程目录不存在，说明是第一个材料，肯定唯一
            if not course_dir.exists():
                logger.info(f"课程目录不存在，course_material_id唯一: {course_id}/{course_material_id}")
                return True
            
            # 检查目录中是否存在以course_material_id开头的文件
            existing_files = []
            if course_dir.is_dir():
                for file_path in course_dir.iterdir():
                    if file_path.is_file():
                        filename = file_path.name
                        # 检查文件名是否以 course_material_id_ 开头
                        if filename.startswith(f"{course_material_id}_"):
                            existing_files.append(filename)
            
            if existing_files:
                logger.warning(f"course_material_id已存在: {course_id}/{course_material_id}, 现有文件: {existing_files}")
                raise HTTPException(
                    status_code=400,
                    detail=f"课程材料ID '{course_material_id}' 在课程 '{course_id}' 中已存在。现有文件: {', '.join(existing_files)}"
                )
            
            logger.info(f"course_material_id验证通过: {course_id}/{course_material_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"验证course_material_id时发生错误: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"验证课程材料ID时发生错误: {str(e)}"
            )
    
    @staticmethod
    def get_existing_material_ids(
        course_id: str,
        uploads_base_dir: Path = UPLOADS_DIR
    ) -> List[str]:
        """
        获取指定课程下已存在的所有material_id
        
        Args:
            course_id: 课程ID
            uploads_base_dir: 上传文件基础目录
            
        Returns:
            已存在的material_id列表
        """
        try:
            course_dir = uploads_base_dir / course_id
            material_ids = []
            
            if course_dir.exists() and course_dir.is_dir():
                for file_path in course_dir.iterdir():
                    if file_path.is_file():
                        filename = file_path.name
                        # 解析文件名格式: {course_material_id}_{material_name}{extension}
                        if '_' in filename:
                            material_id = filename.split('_')[0]
                            if material_id not in material_ids:
                                material_ids.append(material_id)
            
            logger.debug(f"课程 {course_id} 现有material_ids: {material_ids}")
            return material_ids
            
        except Exception as e:
            logger.error(f"获取现有material_ids时发生错误: {str(e)}")
            return []


class FileValidation:
    """文件验证工具类"""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """
        验证文件扩展名
        
        Args:
            filename: 文件名
            allowed_extensions: 允许的扩展名列表
            
        Returns:
            是否有效
        """
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in [ext.lower() for ext in allowed_extensions]
    
    @staticmethod
    def validate_filename_characters(filename: str) -> bool:
        """
        验证文件名字符是否安全
        
        Args:
            filename: 文件名
            
        Returns:
            是否安全
        """
        if not filename:
            return False
        
        # 检查危险字符
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in filename:
                return False
        
        return True
