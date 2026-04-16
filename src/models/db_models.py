"""
数据库模型定义
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class UserSession(Base):
    """用户会话模型"""
    
    __tablename__ = "user_sessions"
    
    id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ip_address = Column(String(45), nullable=True)  # 支持 IPv6
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # 关系
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """聊天消息模型"""
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("user_sessions.id"), index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    model = Column(String(50), nullable=True)  # 使用的模型
    tokens = Column(Integer, nullable=True)  # 使用的 token 数量
    metadata = Column(JSON, nullable=True)  # 额外元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    session = relationship("UserSession", back_populates="messages")

class ModelUsage(Base):
    """模型使用统计"""
    
    __tablename__ = "model_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(50), nullable=False, index=True)
    session_id = Column(String(64), ForeignKey("user_sessions.id"), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Integer, default=0)  # 成本（分）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemLog(Base):
    """系统日志"""
    
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())