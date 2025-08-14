"""
API v1 路由包
"""
from fastapi import APIRouter
from .outline import router as outline_router
from .rag import router as rag_router

api_router = APIRouter()

# 注册路由
api_router.include_router(outline_router)
api_router.include_router(rag_router)
api_router.include_router(rag_router)