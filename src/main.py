#!/usr/bin/env python3
"""
FastAPI 主应用 - 智能问答客服系统
"""

import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn

from src.core.config import settings
from src.core.logging import setup_logging
from src.api.api_v1.api import api_router
from src.core.middleware import setup_middleware
from src.database.session import init_db

# 设置日志
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("🚀 启动智能问答客服系统...")
    logger.info(f"环境: {settings.ENVIRONMENT}")
    logger.info(f"调试模式: {settings.DEBUG}")
    
    # 初始化数据库
    await init_db()
    
    yield
    
    # 关闭时
    logger.info("👋 关闭智能问答客服系统...")

# 创建 FastAPI 应用
app = FastAPI(
    title="Hermes 智能问答客服系统",
    description="基于 FastAPI + LangGraph 的多模型智能问答客服系统",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# 设置中间件
setup_middleware(app)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="src/templates")

# 包含 API 路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root(request: Request):
    """根路由 - 重定向到聊天界面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/chatbot")

@app.get("/chatbot")
async def chatbot(request: Request):
    """聊天机器人页面"""
    from src.services.model_service import get_available_models
    from src.services.session_service import get_or_create_session
    
    # 获取或创建用户会话
    session_id = request.cookies.get("session_id")
    user_session = await get_or_create_session(session_id)
    
    # 获取可用模型
    available_models = await get_available_models()
    
    return templates.TemplateResponse(
        "chatbot/index.html",
        {
            "request": request,
            "user_id": user_session.id,
            "models": available_models,
            "history": user_session.history
        }
    )

@app.get("/health")
async def health_check():
    """健康检查端点"""
    from src.services.health_service import check_health
    
    health_status = await check_health()
    return health_status

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )