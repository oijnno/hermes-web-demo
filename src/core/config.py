"""
应用配置管理
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator, Field

class Settings(BaseSettings):
    """应用设置"""
    
    # 基础配置
    PROJECT_NAME: str = "Hermes 智能问答客服系统"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=5000, env="PORT")
    
    # 安全配置
    SECRET_KEY: str = Field(default="your-secret-key-here-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 配置
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5000"], env="CORS_ORIGINS")
    
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite:///./hermes_chatbot.db", env="DATABASE_URL")
    
    # Redis 配置
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # AI 模型配置
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com/v1", env="DEEPSEEK_BASE_URL")
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat", env="DEEPSEEK_MODEL")
    
    MINIMAX_API_KEY: Optional[str] = Field(default=None, env="MINIMAX_API_KEY")
    MINIMAX_BASE_URL: str = Field(default="https://api.minimax.chat/v1", env="MINIMAX_BASE_URL")
    MINIMAX_MODEL: str = Field(default="abab5.5-chat", env="MINIMAX_MODEL")
    
    QWEN_API_KEY: Optional[str] = Field(default=None, env="QWEN_API_KEY")
    QWEN_BASE_URL: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", env="QWEN_BASE_URL")
    QWEN_MODEL: str = Field(default="qwen-max", env="QWEN_MODEL")
    
    # 模型参数
    MODEL_TEMPERATURE: float = Field(default=0.7, env="MODEL_TEMPERATURE")
    MODEL_MAX_TOKENS: int = Field(default=2000, env="MODEL_MAX_TOKENS")
    
    # 会话配置
    SESSION_EXPIRE_HOURS: int = Field(default=24, env="SESSION_EXPIRE_HOURS")
    MAX_HISTORY_MESSAGES: int = Field(default=20, env="MAX_HISTORY_MESSAGES")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Celery 配置
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()