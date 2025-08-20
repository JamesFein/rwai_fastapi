"""
API v1 路由包
"""
from fastapi import APIRouter
from .outline import router as outline_router
from .rag import router as rag_router
from .course_materials import router as course_materials_router
from .chat import router as chat_router
from .conversation import router as conversation_router

api_router = APIRouter()

# 注册路由
api_router.include_router(outline_router)
api_router.include_router(rag_router)
api_router.include_router(course_materials_router)
api_router.include_router(chat_router)
api_router.include_router(conversation_router)