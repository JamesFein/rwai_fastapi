"""
API v1 路由包
"""
from fastapi import APIRouter
from .outline import router as outline_router
from .rag import router as rag_router
from .course_materials import router as course_materials_router
from .chat import router as chat_router
from .rag_v2 import router as rag_v2_router
from .conversation_v2 import router as conversation_v2_router

api_router = APIRouter()

# 注册路由
api_router.include_router(outline_router)
api_router.include_router(rag_router)
api_router.include_router(course_materials_router)
api_router.include_router(chat_router)

# 注册新版本API路由
api_router.include_router(rag_v2_router)
api_router.include_router(conversation_v2_router)