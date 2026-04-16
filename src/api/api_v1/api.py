"""
API 路由器聚合
"""

from fastapi import APIRouter

from src.api.routes import chat

api_router = APIRouter()

# 包含聊天相关路由
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])