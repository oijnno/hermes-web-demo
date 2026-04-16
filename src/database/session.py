"""
数据库会话管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=settings.DEBUG,
    poolclass=NullPool,  # SQLite 不需要连接池
    future=True
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """初始化数据库"""
    from src.models.db_models import Base
    
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ 数据库初始化完成")