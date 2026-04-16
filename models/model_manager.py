#!/usr/bin/env python3
"""
模型管理器 - 处理 DeepSeek、MiniMax 和 Qwen 三种模型的调用
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime

class ModelManager:
    """管理三种不同的 AI 模型"""
    
    def __init__(self):
        self.models = {
            "deepseek": {
                "name": "DeepSeek",
                "provider": "deepseek",
                "base_url": "https://api.deepseek.com/v1",
                "api_key_env": "DEEPSEEK_API_KEY"
            },
            "minimax": {
                "name": "MiniMax",
                "provider": "minimax",
                "base_url": "https://api.minimax.chat/v1",
                "api_key_env": "MINIMAX_API_KEY"
            },
            "qwen": {
                "name": "Qwen",
                "provider": "qwen",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key_env": "QWEN_API_KEY"
            }
        }
        
        # 检查环境变量
        self.check_api_keys()
    
    def check_api_keys(self):
        """检查 API 密钥是否设置"""
        missing_keys = []
        for model_id, config in self.models.items():
            api_key = os.getenv(config["api_key_env"])
            if not api_key:
                missing_keys.append(f"{config['name']} ({config['api_key_env']})")
        
        if missing_keys:
            print(f"警告: 以下 API 密钥未设置: {', '.join(missing_keys)}")
            print("部分模型可能无法正常工作")
    
    def get_available_models(self) -> list:
        """获取可用的模型列表"""
        available = []
        for model_id, config in self.models.items():
            api_key = os.getenv(config["api_key_env"])
            if api_key:
                available.append({
                    "id": model_id,
                    "name": config["name"],
                    "provider": config["provider"],
                    "available": True
                })
            else:
                available.append({
                    "id": model_id,
                    "name": config["name"],
                    "provider": config["provider"],
                    "available": False
                })
        return available
    
    def call_deepseek(self, prompt: str, history: list = None) -> Dict[str, Any]:
        """调用 DeepSeek 模型"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return {"error": "DeepSeek API 密钥未设置"}
        
        url = f"{self.models['deepseek']['base_url']}/chat/completions"
        
        messages = []
        if history:
            for msg in history[-10:]:  # 只保留最近10条历史记录
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
        
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "content": result["choices"][0]["message"]["content"],
                "model": "deepseek-chat",
                "tokens": result.get("usage", {}),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"DeepSeek API 调用失败: {str(e)}"}
    
    def call_minimax(self, prompt: str, history: list = None) -> Dict[str, Any]:
        """调用 MiniMax 模型"""
        api_key = os.getenv("MINIMAX_API_KEY")
        if not api_key:
            return {"error": "MiniMax API 密钥未设置"}
        
        url = f"{self.models['minimax']['base_url']}/chat/completion"
        
        messages = []
        if history:
            for msg in history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "abab5.5-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "content": result["choices"][0]["message"]["content"],
                "model": "abab5.5-chat",
                "tokens": result.get("usage", {}),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"MiniMax API 调用失败: {str(e)}"}
    
    def call_qwen(self, prompt: str, history: list = None) -> Dict[str, Any]:
        """调用 Qwen 模型"""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            return {"error": "Qwen API 密钥未设置"}
        
        url = f"{self.models['qwen']['base_url']}/chat/completions"
        
        messages = []
        if history:
            for msg in history[-10:]:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
        
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "qwen-max",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "content": result["choices"][0]["message"]["content"],
                "model": "qwen-max",
                "tokens": result.get("usage", {}),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Qwen API 调用失败: {str(e)}"}
    
    def call_model(self, model_id: str, prompt: str, history: list = None) -> Dict[str, Any]:
        """调用指定模型"""
        if model_id not in self.models:
            return {"error": f"未知模型: {model_id}"}
        
        if model_id == "deepseek":
            return self.call_deepseek(prompt, history)
        elif model_id == "minimax":
            return self.call_minimax(prompt, history)
        elif model_id == "qwen":
            return self.call_qwen(prompt, history)
        else:
            return {"error": f"模型 {model_id} 未实现"}