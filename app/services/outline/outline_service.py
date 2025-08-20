"""
大纲生成服务模块
处理文档大纲生成的核心业务逻辑
"""
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import aiofiles
from openai import AsyncOpenAI

from ...core.config import get_settings
from ...core.logging import get_logger
from ...core.deps import generate_filename, read_text_file, write_text_file
from ...schemas.outline import TaskStatus, OutlineGenerateResponse
from ...constants.paths import OUTLINES_DIR, PROMPTS_DIR
from ...utils.idgen import IDGenerator, path_generator

logger = get_logger("outline_service")


class OutlineService:
    """大纲生成服务类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=self.settings.api_key,
            base_url=self.settings.base_url
        )
        
        # 加载提示词模板
        self._outline_prompt_template = None
        self._refine_prompt_template = None
    
    async def _load_prompt_template(self, template_file: str) -> str:
        """加载提示词模板"""
        template_path = PROMPTS_DIR / template_file
        try:
            async with aiofiles.open(template_path, 'r', encoding='utf-8') as f:
                template = await f.read()
            logger.info(f"提示词模板加载成功: {template_file}")
            return template
        except Exception as e:
            logger.error(f"提示词模板加载失败: {template_file}, 错误: {str(e)}")
            raise
    
    async def get_outline_prompt_template(self) -> str:
        """获取大纲生成提示词模板"""
        if self._outline_prompt_template is None:
            self._outline_prompt_template = await self._load_prompt_template("outline_generation.txt")
        return self._outline_prompt_template

    async def get_refine_prompt_template(self) -> str:
        """获取大纲精简提示词模板"""
        if self._refine_prompt_template is None:
            self._refine_prompt_template = await self._load_prompt_template("outline_refine.txt")
        return self._refine_prompt_template
    
    async def generate_outline_from_text(
        self,
        content: str,
        task_id: str,
        custom_prompt: Optional[str] = None,
        include_refine: bool = True,
        model_name: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        从文本内容生成大纲
        
        Args:
            content: 文档内容
            task_id: 任务ID
            custom_prompt: 自定义提示词
            include_refine: 是否进行精简处理
            model_name: 模型名称
            
        Returns:
            Tuple[生成的大纲内容, Token使用统计]
        """
        start_time = time.time()
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        try:
            # 第一阶段：生成原始大纲
            if custom_prompt:
                prompt = custom_prompt.replace("{content}", content)
            else:
                template = await self.get_outline_prompt_template()
                prompt = template.replace("{content}", content)
            
            model = model_name or self.settings.outline_model
            
            logger.info(f"开始生成大纲 - 任务ID: {task_id}, 模型: {model}, 内容长度: {len(content)}")
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            raw_outline = response.choices[0].message.content
            
            # 累计Token使用
            if hasattr(response, 'usage') and response.usage:
                total_tokens["prompt_tokens"] += response.usage.prompt_tokens
                total_tokens["completion_tokens"] += response.usage.completion_tokens
                total_tokens["total_tokens"] += response.usage.total_tokens
            
            logger.info(f"原始大纲生成完成 - 任务ID: {task_id}, 长度: {len(raw_outline)}")
            
            # 第二阶段：精简大纲（如果需要）
            if include_refine:
                refine_template = await self.get_refine_prompt_template()
                refine_prompt = refine_template.replace("{raw_outline}", raw_outline)
                
                refine_model = model_name or self.settings.refine_model
                
                logger.info(f"开始精简大纲 - 任务ID: {task_id}, 模型: {refine_model}")
                
                refine_response = await self.client.chat.completions.create(
                    model=refine_model,
                    messages=[
                        {"role": "user", "content": refine_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=3000
                )
                
                final_outline = refine_response.choices[0].message.content
                
                # 累计Token使用
                if hasattr(refine_response, 'usage') and refine_response.usage:
                    total_tokens["prompt_tokens"] += refine_response.usage.prompt_tokens
                    total_tokens["completion_tokens"] += refine_response.usage.completion_tokens
                    total_tokens["total_tokens"] += refine_response.usage.total_tokens
                
                logger.info(f"大纲精简完成 - 任务ID: {task_id}, 最终长度: {len(final_outline)}")
            else:
                final_outline = raw_outline
                logger.info(f"跳过大纲精简 - 任务ID: {task_id}")
            
            processing_time = time.time() - start_time
            logger.info(f"大纲生成总耗时: {processing_time:.2f}秒 - 任务ID: {task_id}")
            
            return final_outline, total_tokens
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"大纲生成失败 - 任务ID: {task_id}, 耗时: {processing_time:.2f}秒, 错误: {str(e)}")
            raise
    
    async def save_outline_to_file(
        self,
        outline_content: str,
        task_id: str,
        original_filename: str,
        course_id: Optional[str] = None,
        course_material_id: Optional[str] = None,
        material_name: Optional[str] = None
    ) -> str:
        """
        保存大纲到文件

        Args:
            outline_content: 大纲内容
            task_id: 任务ID
            original_filename: 原始文件名
            course_id: 课程ID (新增)
            course_material_id: 课程材料ID (新增)
            material_name: 材料名称 (新增)

        Returns:
            保存的文件路径
        """
        try:
            # 如果提供了课程信息，使用新的路径生成方式
            if course_id and course_material_id and material_name:
                outline_path = path_generator.generate_course_outline_path(
                    base_dir=OUTLINES_DIR,
                    course_id=course_id,
                    course_material_id=course_material_id,
                    material_name=material_name
                )
            else:
                # 兼容旧的路径生成方式
                outline_filename = generate_filename(
                    f"outline_{Path(original_filename).stem}.md",
                    task_id
                )
                outline_path = OUTLINES_DIR / outline_filename

            # 确保目录存在
            outline_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存文件
            await write_text_file(outline_path, outline_content)

            logger.info(f"大纲文件保存成功 - 任务ID: {task_id}, 路径: {outline_path}")

            return str(outline_path)

        except Exception as e:
            logger.error(f"大纲文件保存失败 - 任务ID: {task_id}, 错误: {str(e)}")
            raise
    
    async def process_outline_generation(
        self,
        file_content: str,
        original_filename: str,
        custom_prompt: Optional[str] = None,
        include_refine: bool = True,
        model_name: Optional[str] = None,
        course_id: Optional[str] = None,
        course_material_id: Optional[str] = None,
        material_name: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> OutlineGenerateResponse:
        """
        处理完整的大纲生成流程

        Args:
            file_content: 文件内容
            original_filename: 原始文件名
            custom_prompt: 自定义提示词
            include_refine: 是否精简
            model_name: 模型名称
            course_id: 课程ID (新增)
            course_material_id: 课程材料ID (新增)
            material_name: 材料名称 (新增)
            task_id: 任务ID (可选，如果不提供则自动生成)

        Returns:
            大纲生成响应
        """
        if task_id is None:
            task_id = IDGenerator.generate_task_id()
        start_time = time.time()
        
        try:
            logger.info(f"开始处理大纲生成 - 任务ID: {task_id}, 文件: {original_filename}")
            
            # 生成大纲
            outline_content, token_usage = await self.generate_outline_from_text(
                content=file_content,
                task_id=task_id,
                custom_prompt=custom_prompt,
                include_refine=include_refine,
                model_name=model_name
            )
            
            # 保存大纲文件
            outline_file_path = await self.save_outline_to_file(
                outline_content=outline_content,
                task_id=task_id,
                original_filename=original_filename,
                course_id=course_id,
                course_material_id=course_material_id,
                material_name=material_name
            )

            processing_time = time.time() - start_time

            response = OutlineGenerateResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                message="大纲生成成功",
                course_id=course_id,
                course_material_id=course_material_id,
                material_name=material_name,
                outline_content=outline_content,
                outline_file_path=outline_file_path,
                processing_time=processing_time,
                token_usage=token_usage,
                completed_at=time.time()
            )
            
            logger.info(f"大纲生成流程完成 - 任务ID: {task_id}, 总耗时: {processing_time:.2f}秒")
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"大纲生成流程失败 - 任务ID: {task_id}, 耗时: {processing_time:.2f}秒, 错误: {str(e)}")
            
            return OutlineGenerateResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                message=f"大纲生成失败: {str(e)}",
                processing_time=processing_time
            )


# 全局服务实例
outline_service = OutlineService()
