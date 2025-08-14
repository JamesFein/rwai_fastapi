"""
时间处理工具模块
提供时间戳、计时器等功能
"""
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncio

from ..core.logging import get_logger

logger = get_logger("timers")


class Timer:
    """计时器类"""
    
    def __init__(self, name: str = "Timer"):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_time: Optional[float] = None
    
    def start(self) -> 'Timer':
        """开始计时"""
        self.start_time = time.time()
        self.end_time = None
        self.elapsed_time = None
        logger.debug(f"{self.name} 开始计时")
        return self
    
    def stop(self) -> float:
        """停止计时并返回耗时"""
        if self.start_time is None:
            raise ValueError("计时器未启动")
        
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        logger.debug(f"{self.name} 计时结束，耗时: {self.elapsed_time:.3f}秒")
        return self.elapsed_time
    
    def get_elapsed(self) -> float:
        """获取已耗时间（不停止计时器）"""
        if self.start_time is None:
            return 0.0
        
        current_time = time.time()
        return current_time - self.start_time
    
    def reset(self) -> 'Timer':
        """重置计时器"""
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        logger.debug(f"{self.name} 计时器已重置")
        return self
    
    def __enter__(self) -> 'Timer':
        """上下文管理器入口"""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


class AsyncTimer:
    """异步计时器类"""
    
    def __init__(self, name: str = "AsyncTimer"):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_time: Optional[float] = None
    
    async def start(self) -> 'AsyncTimer':
        """开始计时"""
        self.start_time = time.time()
        self.end_time = None
        self.elapsed_time = None
        logger.debug(f"{self.name} 开始计时")
        return self
    
    async def stop(self) -> float:
        """停止计时并返回耗时"""
        if self.start_time is None:
            raise ValueError("计时器未启动")
        
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        logger.debug(f"{self.name} 计时结束，耗时: {self.elapsed_time:.3f}秒")
        return self.elapsed_time
    
    async def get_elapsed(self) -> float:
        """获取已耗时间（不停止计时器）"""
        if self.start_time is None:
            return 0.0
        
        current_time = time.time()
        return current_time - self.start_time
    
    async def __aenter__(self) -> 'AsyncTimer':
        """异步上下文管理器入口"""
        return await self.start()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def record_timing(self, operation: str, elapsed_time: float, **metadata):
        """记录操作耗时"""
        if operation not in self.metrics:
            self.metrics[operation] = {
                "count": 0,
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "avg_time": 0.0,
                "last_time": 0.0,
                "metadata": []
            }
        
        metric = self.metrics[operation]
        metric["count"] += 1
        metric["total_time"] += elapsed_time
        metric["min_time"] = min(metric["min_time"], elapsed_time)
        metric["max_time"] = max(metric["max_time"], elapsed_time)
        metric["avg_time"] = metric["total_time"] / metric["count"]
        metric["last_time"] = elapsed_time
        
        if metadata:
            metric["metadata"].append({
                "timestamp": datetime.now().isoformat(),
                "elapsed_time": elapsed_time,
                **metadata
            })
        
        logger.info(f"性能记录 - {operation}: {elapsed_time:.3f}秒 (平均: {metric['avg_time']:.3f}秒)")
    
    def get_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """获取性能指标"""
        if operation:
            return self.metrics.get(operation, {})
        return self.metrics
    
    def reset_metrics(self, operation: Optional[str] = None):
        """重置性能指标"""
        if operation:
            if operation in self.metrics:
                del self.metrics[operation]
                logger.info(f"已重置 {operation} 的性能指标")
        else:
            self.metrics.clear()
            logger.info("已重置所有性能指标")


class TimestampUtils:
    """时间戳工具类"""
    
    @staticmethod
    def get_current_timestamp() -> float:
        """获取当前时间戳"""
        return time.time()
    
    @staticmethod
    def get_current_datetime() -> datetime:
        """获取当前日期时间"""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def timestamp_to_datetime(timestamp: float) -> datetime:
        """时间戳转日期时间"""
        return datetime.fromtimestamp(timestamp, timezone.utc)
    
    @staticmethod
    def datetime_to_timestamp(dt: datetime) -> float:
        """日期时间转时间戳"""
        return dt.timestamp()
    
    @staticmethod
    def format_timestamp(timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化时间戳"""
        dt = TimestampUtils.timestamp_to_datetime(timestamp)
        return dt.strftime(format_str)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化持续时间"""
        if seconds < 1:
            return f"{seconds*1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m{secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}h{minutes}m{secs:.1f}s"


@asynccontextmanager
async def async_timer(name: str = "Operation"):
    """异步计时器上下文管理器"""
    timer = AsyncTimer(name)
    await timer.start()
    try:
        yield timer
    finally:
        await timer.stop()


def timer_decorator(name: Optional[str] = None):
    """计时器装饰器"""
    def decorator(func):
        operation_name = name or f"{func.__module__}.{func.__name__}"
        
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                async with async_timer(operation_name) as timer:
                    result = await func(*args, **kwargs)
                    performance_monitor.record_timing(
                        operation_name,
                        timer.elapsed_time,
                        function=func.__name__,
                        args_count=len(args),
                        kwargs_count=len(kwargs)
                    )
                    return result
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                with Timer(operation_name) as timer:
                    result = func(*args, **kwargs)
                    performance_monitor.record_timing(
                        operation_name,
                        timer.elapsed_time,
                        function=func.__name__,
                        args_count=len(args),
                        kwargs_count=len(kwargs)
                    )
                    return result
            return sync_wrapper
    
    return decorator


# 全局实例
performance_monitor = PerformanceMonitor()
timestamp_utils = TimestampUtils()
