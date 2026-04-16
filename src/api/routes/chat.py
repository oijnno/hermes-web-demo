"""
API 路由定义
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.database.session import get_db
from src.schemas.chat_schemas import (
    ChatRequest, ChatResponse, ModelInfo, HealthCheck,
    ErrorResponse, SessionInfo
)
from src.services.model_service import model_service
from src.services.session_service import session_service
from src.services.workflow_service import chatbot_workflow
from src.core.logging import setup_logging

logger = setup_logging()

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查"""
    
    # 获取可用模型
    available_models = await model_service.get_available_models()
    
    # 获取活跃会话数（简化版）
    # 在实际应用中，这里应该查询数据库
    
    return {
        "status": "healthy",
        "service": "hermes-chatbot",
        "version": "1.0.0",
        "models": available_models,
        "active_sessions": 0,  # 暂时返回0
        "timestamp": datetime.now()
    }

@router.get("/models", response_model=List[ModelInfo])
async def get_models():
    """获取可用模型列表"""
    
    models_data = await model_service.get_available_models()
    return models_data

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
):
    """处理聊天请求"""
    
    try:
        # 获取或创建会话
        session = await session_service.get_or_create_session(
            db,
            request.session_id,
            ip_address=http_request.client.host if http_request else None,
            user_agent=http_request.headers.get("user-agent") if http_request else None
        )
        
        # 获取会话历史
        history_messages = await session_service.get_session_history(db, session.id)
        history = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in history_messages
        ]
        
        # 运行工作流
        result = await chatbot_workflow.run(
            request.model,
            request.message,
            history
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        # 保存消息到数据库
        await session_service.add_message(
            db,
            session.id,
            "user",
            request.message,
            model=request.model
        )
        
        await session_service.add_message(
            db,
            session.id,
            "assistant",
            result["response"],
            model=request.model,
            tokens=result.get("tokens", {}).get("total_tokens") if result.get("tokens") else None
        )
        
        return {
            "success": True,
            "response": result["response"],
            "model": request.model,
            "session_id": session.id,
            "tokens": result.get("tokens"),
            "timestamp": datetime.fromisoformat(result["timestamp"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天请求处理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """获取聊天历史"""
    
    try:
        messages = await session_service.get_session_history(
            db, session_id, limit, offset
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "model": msg.model,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ],
            "total": len(messages),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史失败: {str(e)}"
        )

@router.post("/clear/{session_id}")
async def clear_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """清空聊天历史"""
    
    try:
        deleted_count = await session_service.clear_session_history(db, session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "deleted_count": deleted_count,
            "message": "聊天历史已清空",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"清空历史失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空历史失败: {str(e)}"
        )

@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session_info(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取会话信息"""
    
    try:
        session_info = await session_service.get_session_info(db, session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话信息失败: {str(e)}"
        )

@router.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.now().isoformat()
        }
    )

@router.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    
    logger.error(f"未处理的异常: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "服务器内部错误",
            "code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    )