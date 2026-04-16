"""
Pydantic 数据模式
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MessageBase(BaseModel):
    """消息基础模式"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")
    model: Optional[str] = Field(None, description="使用的模型")

class MessageCreate(MessageBase):
    """创建消息"""
    pass

class MessageResponse(MessageBase):
    """消息响应"""
    id: int
    session_id: str
    created_at: datetime
    tokens: Optional[int] = None
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """聊天请求"""
    model: str = Field(..., description="模型名称: deepseek, minimax, qwen")
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")
    stream: bool = Field(False, description="是否使用流式响应")

class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool = Field(..., description="是否成功")
    response: Optional[str] = Field(None, description="AI响应内容")
    model: str = Field(..., description="使用的模型")
    session_id: str = Field(..., description="会话ID")
    tokens: Optional[Dict[str, int]] = Field(None, description="token使用情况")
    timestamp: datetime = Field(..., description="响应时间")

class ModelInfo(BaseModel):
    """模型信息"""
    id: str = Field(..., description="模型ID")
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    available: bool = Field(..., description="是否可用")
    description: Optional[str] = Field(None, description="模型描述")

class HealthCheck(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本号")
    models: List[ModelInfo] = Field(..., description="可用模型")
    active_sessions: int = Field(..., description="活跃会话数")
    timestamp: datetime = Field(..., description="检查时间")

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(False, description="是否成功")
    error: str = Field(..., description="错误信息")
    code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(..., description="错误时间")

class SessionInfo(BaseModel):
    """会话信息"""
    id: str = Field(..., description="会话ID")
    created_at: datetime = Field(..., description="创建时间")
    last_active: datetime = Field(..., description="最后活跃时间")
    message_count: int = Field(..., description="消息数量")
    is_active: bool = Field(..., description="是否活跃")