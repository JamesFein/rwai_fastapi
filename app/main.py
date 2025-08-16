"""
FastAPI 主应用文件
AI功能后端的入口点
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import get_settings
from .core.logging import setup_logging, get_logger
from .constants.paths import ensure_directories
from .api.v1 import api_router
from .schemas.outline import ErrorResponse, HealthResponse
from . import __version__, __description__

# 设置日志
setup_logging()
logger = get_logger("main")

# 应用启动时间
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 AI Backend 应用启动中...")
    
    # 获取配置
    settings = get_settings()
    
    # 确保目录存在
    try:
        ensure_directories()
        settings.ensure_directories()
        logger.info("✅ 目录结构检查完成")
    except Exception as e:
        logger.error(f"❌ 目录创建失败: {str(e)}")
        raise
    
    # 验证配置
    try:
        logger.info(f"📋 配置验证 - API密钥: {settings.api_key[:10]}...")
        logger.info(f"📋 配置验证 - 基础URL: {settings.base_url}")
        logger.info(f"📋 配置验证 - 大纲模型: {settings.outline_model}")
        logger.info(f"📋 配置验证 - 精简模型: {settings.refine_model}")
        logger.info("✅ 配置验证完成")
    except Exception as e:
        logger.error(f"❌ 配置验证失败: {str(e)}")
        raise
    
    logger.info("🎉 AI Backend 应用启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("🛑 AI Backend 应用关闭中...")
    logger.info("👋 AI Backend 应用已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI Backend API",
    description=__description__,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 获取配置
settings = get_settings()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()
    
    # 记录请求开始
    logger.info(f"📥 {request.method} {request.url.path} - 开始处理")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"状态: {response.status_code}, 耗时: {process_time:.3f}s"
    )
    
    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="http_error",
            message=exc.detail,
            detail=f"HTTP {exc.status_code}"
        ).model_dump(mode="json")
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.error(f"请求验证失败: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="validation_error",
            message="请求参数验证失败",
            detail=str(exc.errors())
        ).model_dump(mode="json")
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {type(exc).__name__} - {str(exc)}")

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_error",
            message="服务器内部错误",
            detail=str(exc) if settings.debug else "请联系管理员"
        ).model_dump(mode="json")
    )


# 根路径
@app.get("/", summary="根路径", description="API根路径，返回基本信息")
async def root():
    """根路径"""
    return {
        "name": "AI Backend API",
        "version": __version__,
        "description": __description__,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health"
    }


# 健康检查
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务健康状态"
)
async def health_check():
    """健康检查"""
    uptime = time.time() - app_start_time
    
    # 检查 OpenAI API 连接（简单检查）
    openai_status = "unknown"
    try:
        # 这里可以添加实际的 OpenAI API 连接检查
        # 为了避免频繁调用，这里只是简单检查配置
        if settings.api_key and settings.base_url:
            openai_status = "configured"
        else:
            openai_status = "not_configured"
    except Exception:
        openai_status = "error"
    
    return HealthResponse(
        status="healthy",
        version=__version__,
        uptime=uptime,
        openai_api=openai_status
    )


# 注册路由
app.include_router(
    api_router,
    prefix=settings.api_v1_prefix
)

# 挂载静态文件
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"✅ 静态文件服务已启用: {static_dir}")
else:
    logger.warning(f"⚠️ 静态文件目录不存在: {static_dir}")


# 如果直接运行此文件
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 启动开发服务器 - {settings.host}:{settings.port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
