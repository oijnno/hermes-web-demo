"""
模型服务 - 处理 DeepSeek、MiniMax 和 Qwen 三种模型的调用
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from openai import AsyncOpenAI

from src.core.config import settings
from src.core.logging import setup_logging

logger = setup_logging()

class ModelService:
    """模型服务"""
    
    def __init__(self):
        self.models = {
            "deepseek": {
                "name": "DeepSeek",
                "provider": "deepseek",
                "base_url": settings.DEEPSEEK_BASE_URL,
                "api_key": settings.DEEPSEEK_API_KEY,
                "model": settings.DEEPSEEK_MODEL,
                "client": None
            },
            "minimax": {
                "name": "MiniMax",
                "provider": "minimax",
                "base_url": settings.MINIMAX_BASE_URL,
                "api_key": settings.MINIMAX_API_KEY,
                "model": settings.MINIMAX_MODEL,
                "client": None
            },
            "qwen": {
                "name": "Qwen",
                "provider": "qwen",
                "base_url": settings.QWEN_BASE_URL,
                "api_key": settings.QWEN_API_KEY,
                "model": settings.QWEN_MODEL,
                "client": None
            }
        }
        
        # 初始化 OpenAI 兼容客户端
        self._init_clients()
    
    def _init_clients(self):
        """初始化 OpenAI 兼容客户端"""
        for model_id, config in self.models.items():
            if config["api_key"]:
                try:
                    config["client"] = AsyncOpenAI(
                        api_key=config["api_key"],
                        base_url=config["base_url"]
                    )
                    logger.info(f"✅ {config['name']} 客户端初始化成功")
                except Exception as e:
                    logger.error(f"❌ {config['name']} 客户端初始化失败: {e}")
                    config["client"] = None
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        available = []
        
        for model_id, config in self.models.items():
            is_available = bool(config["api_key"] and config["client"])
            
            # 测试连接（可选）
            if is_available:
                try:
                    # 简单的连接测试
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            config["base_url"],
                            headers={"Authorization": f"Bearer {config['api_key']}"},
                            timeout=5
                        ) as response:
                            if response.status != 200:
                                is_available = False
                except:
                    is_available = False
            
            available.append({
                "id": model_id,
                "name": config["name"],
                "provider": config["provider"],
                "available": is_available,
                "description": self._get_model_description(model_id)
            })
        
        return available
    
    def _get_model_description(self, model_id: str) -> str:
        """获取模型描述"""
        descriptions = {
            "deepseek": "擅长代码编程和技术问题解答",
            "minimax": "创意写作和对话生成专家",
            "qwen": "中文理解和多轮对话优化"
        }
        return descriptions.get(model_id, "AI 助手")
    
    async def call_model(
        self,
        model_id: str,
        prompt: str,
        history: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """调用指定模型"""
        
        if model_id not in self.models:
            return {"error": f"未知模型: {model_id}"}
        
        config = self.models[model_id]
        
        if not config["api_key"] or not config["client"]:
            return {"error": f"{config['name']} API 密钥未配置"}
        
        try:
            # 构建消息列表
            messages = []
            
            # 添加历史消息
            if history:
                for msg in history[-10:]:  # 只保留最近10条
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # 添加当前消息
            messages.append({"role": "user", "content": prompt})
            
            # 调用模型
            response = await config["client"].chat.completions.create(
                model=config["model"],
                messages=messages,
                temperature=settings.MODEL_TEMPERATURE,
                max_tokens=settings.MODEL_MAX_TOKENS,
                stream=False,
                **kwargs
            )
            
            # 提取响应
            content = response.choices[0].message.content
            usage = response.usage
            
            return {
                "content": content,
                "model": config["model"],
                "tokens": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                } if usage else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"调用 {config['name']} 模型失败: {e}")
            return {"error": f"{config['name']} API 调用失败: {str(e)}"}
    
    async def call_deepseek(self, prompt: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """调用 DeepSeek 模型"""
        return await self.call_model("deepseek", prompt, history)
    
    async def call_minimax(self, prompt: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """调用 MiniMax 模型"""
        return await self.call_model("minimax", prompt, history)
    
    async def call_qwen(self, prompt: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """调用 Qwen 模型"""
        return await self.call_model("qwen", prompt, history)

# 创建全局模型服务实例
model_service = ModelService()