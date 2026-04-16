"""
会话服务 - 管理用户会话和聊天历史
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.models.db_models import UserSession, ChatMessage
from src.core.config import settings
from src.core.logging import setup_logging

logger = setup_logging()

class SessionService:
    """会话服务"""
    
    def __init__(self):
        pass
    
    async def get_or_create_session(
        self,
        db: AsyncSession,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """获取或创建用户会话"""
        
        if session_id:
            # 查找现有会话
            stmt = select(UserSession).where(
                UserSession.id == session_id,
                UserSession.is_active == True
            )
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if session:
                # 更新最后活跃时间
                session.last_active = datetime.utcnow()
                await db.commit()
                await db.refresh(session)
                return session
        
        # 创建新会话
        new_session_id = str(uuid.uuid4())
        session = UserSession(
            id=new_session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"创建新会话: {new_session_id}")
        return session
    
    async def add_message(
        self,
        db: AsyncSession,
        session_id: str,
        role: str,
        content: str,
        model: Optional[str] = None,
        tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """添加聊天消息"""
        
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            model=model,
            tokens=tokens,
            metadata=metadata or {}
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        # 更新会话的最后活跃时间
        await self._update_session_activity(db, session_id)
        
        return message
    
    async def get_session_history(
        self,
        db: AsyncSession,
        session_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[ChatMessage]:
        """获取会话历史"""
        
        stmt = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        ).order_by(
            ChatMessage.created_at.asc()
        ).offset(offset).limit(limit)
        
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        return messages
    
    async def clear_session_history(
        self,
        db: AsyncSession,
        session_id: str
    ) -> int:
        """清空会话历史"""
        
        stmt = delete(ChatMessage).where(
            ChatMessage.session_id == session_id
        )
        
        result = await db.execute(stmt)
        await db.commit()
        
        # 更新会话的最后活跃时间
        await self._update_session_activity(db, session_id)
        
        deleted_count = result.rowcount
        logger.info(f"清空会话 {session_id} 的历史，删除 {deleted_count} 条消息")
        
        return deleted_count
    
    async def get_session_info(
        self,
        db: AsyncSession,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        
        stmt = select(UserSession).where(
            UserSession.id == session_id,
            UserSession.is_active == True
        )
        
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        # 获取消息数量
        count_stmt = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        )
        count_result = await db.execute(count_stmt)
        message_count = len(count_result.scalars().all())
        
        return {
            "id": session.id,
            "created_at": session.created_at,
            "last_active": session.last_active,
            "message_count": message_count,
            "is_active": session.is_active
        }
    
    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """清理过期会话"""
        
        expire_time = datetime.utcnow() - timedelta(hours=settings.SESSION_EXPIRE_HOURS)
        
        # 标记过期会话为不活跃
        stmt = update(UserSession).where(
            UserSession.last_active < expire_time,
            UserSession.is_active == True
        ).values(is_active=False)
        
        result = await db.execute(stmt)
        await db.commit()
        
        expired_count = result.rowcount
        if expired_count > 0:
            logger.info(f"清理了 {expired_count} 个过期会话")
        
        return expired_count
    
    async def _update_session_activity(self, db: AsyncSession, session_id: str):
        """更新会话活跃时间"""
        
        stmt = update(UserSession).where(
            UserSession.id == session_id
        ).values(last_active=datetime.utcnow())
        
        await db.execute(stmt)
        await db.commit()

# 创建全局会话服务实例
session_service = SessionService()