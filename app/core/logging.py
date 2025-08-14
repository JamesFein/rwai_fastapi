"""
日志配置模块
使用 loguru 进行结构化日志记录
"""
import sys
from loguru import logger
from typing import Dict, Any
import json
from .config import get_settings


def json_formatter(record: Dict[str, Any]) -> str:
    """JSON格式化器"""
    log_entry = {
        "time": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }

    # 添加额外的上下文信息
    if record.get("extra"):
        log_entry.update(record["extra"])

    return json.dumps(log_entry, ensure_ascii=False)


def text_formatter(record: Dict[str, Any]) -> str:
    """文本格式化器"""
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>\n"
    )


def setup_logging():
    """设置日志配置"""
    settings = get_settings()
    
    # 移除默认的处理器
    logger.remove()
    
    # 选择格式化器 - 暂时使用文本格式避免 JSON 格式化问题
    formatter = text_formatter
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=formatter,
        level=settings.log_level,
        colorize=settings.log_format.lower() != "json",
        backtrace=settings.debug,
        diagnose=settings.debug,
    )
    
    # 在调试模式下，API密钥也会显示在日志中便于调试
    if settings.debug:
        logger.info(f"调试模式已启用，API密钥: {settings.api_key[:10]}...")
        logger.info(f"API基础URL: {settings.base_url}")
    
    logger.info("日志系统初始化完成")
    return logger


def get_logger(name: str = None):
    """获取日志记录器"""
    if name:
        return logger.bind(name=name)
    return logger


# 创建应用日志记录器
app_logger = get_logger("app")
