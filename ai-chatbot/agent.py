#!/usr/bin/env python3
"""
多模型智能问答客服系统
使用 LangGraph 协调 DeepSeek、MiniMax、千问三个模型
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import qianfan

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

class ModelType(Enum):
    """支持的模型类型"""
    DEEPSEEK = "deepseek"
    MINIMAX = "minimax"
    QWEN = "qwen"

@dataclass
class ChatState:
    """对话状态"""
    user_input: str
    conversation_history: List[Dict[str, str]]
    model_responses: Dict[str, str]  # 各模型的响应
    selected_model: Optional[ModelType] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

class MultiModelChatAgent:
    """多模型聊天智能体"""
    
    def __init__(self):
        self.models = self._initialize_models()
        self.graph = self._build_graph()
        
    def _initialize_models(self) -> Dict[ModelType, Any]:
        """初始化所有模型"""
        models = {}
        
        # DeepSeek 模型
        try:
            deepseek_llm = ChatOpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL"),
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                temperature=float(os.getenv("TEMPERATURE", 0.7)),
                max_tokens=int(os.getenv("MAX_TOKENS", 2000))
            )
            models[ModelType.DEEPSEEK] = deepseek_llm
            logger.info("DeepSeek 模型初始化成功")
        except Exception as e:
            logger.warning(f"DeepSeek 模型初始化失败: {e}")
            models[ModelType.DEEPSEEK] = None
        
        # MiniMax 模型 (使用 OpenAI 兼容接口)
        try:
            minimax_llm = ChatOpenAI(
                api_key=os.getenv("MINIMAX_API_KEY"),
                base_url=os.getenv("MINIMAX_BASE_URL"),
                model=os.getenv("MINIMAX_MODEL", "abab6.5s-chat"),
                temperature=float(os.getenv("TEMPERATURE", 0.7)),
                max_tokens=int(os.getenv("MAX_TOKENS", 2000))
            )
            models[ModelType.MINIMAX] = minimax_llm
            logger.info("MiniMax 模型初始化成功")
        except Exception as e:
            logger.warning(f"MiniMax 模型初始化失败: {e}")
            models[ModelType.MINIMAX] = None
        
        # 千问模型 (使用 Qianfan SDK)
        try:
            # 千问需要不同的初始化方式
            models[ModelType.QWEN] = "qwen_initialized"
            logger.info("千问模型标记为可用")
        except Exception as e:
            logger.warning(f"千问模型初始化失败: {e}")
            models[ModelType.QWEN] = None
        
        return models
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图"""
        
        # 创建状态图
        workflow = StateGraph(ChatState)
        
        # 添加节点
        workflow.add_node("parse_input", self._parse_input)
        workflow.add_node("call_deepseek", self._call_deepseek)
        workflow.add_node("call_minimax", self._call_minimax)
        workflow.add_node("call_qwen", self._call_qwen)
        workflow.add_node("aggregate_responses", self._aggregate_responses)
        workflow.add_node("format_output", self._format_output)
        
        # 设置入口点
        workflow.set_entry_point("parse_input")
        
        # 添加边
        workflow.add_edge("parse_input", "call_deepseek")
        workflow.add_edge("parse_input", "call_minimax")
        workflow.add_edge("parse_input", "call_qwen")
        
        # 并行调用所有模型
        workflow.add_edge("call_deepseek", "aggregate_responses")
        workflow.add_edge("call_minimax", "aggregate_responses")
        workflow.add_edge("call_qwen", "aggregate_responses")
        
        workflow.add_edge("aggregate_responses", "format_output")
        workflow.add_edge("format_output", END)
        
        return workflow.compile()
    
    def _parse_input(self, state: ChatState) -> ChatState:
        """解析用户输入"""
        logger.info(f"解析用户输入: {state.user_input[:50]}...")
        
        # 简单的输入清理和验证
        cleaned_input = state.user_input.strip()
        if not cleaned_input:
            raise ValueError("用户输入不能为空")
        
        # 更新对话历史
        new_history = state.conversation_history.copy()
        new_history.append({
            "role": "user",
            "content": cleaned_input,
            "timestamp": datetime.now().isoformat()
        })
        
        state.conversation_history = new_history
        return state
    
    def _call_deepseek(self, state: ChatState) -> ChatState:
        """调用 DeepSeek 模型"""
        if self.models.get(ModelType.DEEPSEEK) is None:
            logger.warning("DeepSeek 模型不可用，跳过")
            state.model_responses[ModelType.DEEPSEEK.value] = "模型不可用"
            return state
        
        try:
            # 构建消息
            messages = self._build_messages(state.conversation_history)
            
            # 调用模型
            response = self.models[ModelType.DEEPSEEK].invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            state.model_responses[ModelType.DEEPSEEK.value] = content
            logger.info(f"DeepSeek 响应生成成功，长度: {len(content)}")
            
        except Exception as e:
            logger.error(f"DeepSeek 调用失败: {e}")
            state.model_responses[ModelType.DEEPSEEK.value] = f"调用失败: {str(e)}"
        
        return state
    
    def _call_minimax(self, state: ChatState) -> ChatState:
        """调用 MiniMax 模型"""
        if self.models.get(ModelType.MINIMAX) is None:
            logger.warning("MiniMax 模型不可用，跳过")
            state.model_responses[ModelType.MINIMAX.value] = "模型不可用"
            return state
        
        try:
            # 构建消息
            messages = self._build_messages(state.conversation_history)
            
            # 调用模型
            response = self.models[ModelType.MINIMAX].invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            state.model_responses[ModelType.MINIMAX.value] = content
            logger.info(f"MiniMax 响应生成成功，长度: {len(content)}")
            
        except Exception as e:
            logger.error(f"MiniMax 调用失败: {e}")
            state.model_responses[ModelType.MINIMAX.value] = f"调用失败: {str(e)}"
        
        return state
    
    def _call_qwen(self, state: ChatState) -> ChatState:
        """调用千问模型"""
        if self.models.get(ModelType.QWEN) is None:
            logger.warning("千问模型不可用，跳过")
            state.model_responses[ModelType.QWEN.value] = "模型不可用"
            return state
        
        try:
            # 使用 Qianfan SDK 调用千问
            import qianfan
            
            # 构建消息
            messages = []
            for msg in state.conversation_history[-10:]:  # 只取最近10条消息
                if msg["role"] == "user":
                    messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    messages.append({"role": "assistant", "content": msg["content"]})
            
            # 添加系统提示
            system_prompt = {
                "role": "system",
                "content": "你是一个有帮助的AI助手。请用中文回答用户的问题。"
            }
            messages.insert(0, system_prompt)
            
            # 调用千问 API
            chat_comp = qianfan.ChatCompletion()
            resp = chat_comp.do(
                model=os.getenv("QWEN_MODEL", "qwen-max"),
                messages=messages,
                temperature=float(os.getenv("TEMPERATURE", 0.7)),
                top_p=0.8
            )
            
            if resp and hasattr(resp, 'body') and 'choices' in resp.body:
                content = resp.body['choices'][0]['message']['content']
                state.model_responses[ModelType.QWEN.value] = content
                logger.info(f"千问响应生成成功，长度: {len(content)}")
            else:
                raise ValueError("千问 API 返回格式异常")
                
        except Exception as e:
            logger.error(f"千问调用失败: {e}")
            state.model_responses[ModelType.QWEN.value] = f"调用失败: {str(e)}"
        
        return state
    
    def _aggregate_responses(self, state: ChatState) -> ChatState:
        """聚合所有模型的响应"""
        logger.info("聚合模型响应...")
        
        # 确保 responses 字典存在
        if not hasattr(state, 'model_responses'):
            state.model_responses = {}
        
        # 记录响应统计
        successful_models = []
        for model_type in ModelType:
            if model_type.value in state.model_responses:
                response = state.model_responses[model_type.value]
                if response and response != "模型不可用" and not response.startswith("调用失败"):
                    successful_models.append(model_type.value)
        
        logger.info(f"成功响应的模型: {successful_models}")
        
        # 添加元数据
        if state.metadata is None:
            state.metadata = {}
        
        state.metadata.update({
            "response_timestamp": datetime.now().isoformat(),
            "successful_models": successful_models,
            "total_models_called": len(ModelType)
        })
        
        return state
    
    def _format_output(self, state: ChatState) -> ChatState:
        """格式化输出"""
        logger.info("格式化输出...")
        
        # 更新对话历史
        for model_type, response in state.model_responses.items():
            if response and response != "模型不可用" and not response.startswith("调用失败"):
                state.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "model": model_type,
                    "timestamp": datetime.now().isoformat()
                })
        
        return state
    
    def _build_messages(self, conversation_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """从对话历史构建消息列表"""
        messages = []
        
        # 添加系统提示
        system_prompt = {
            "role": "system",
            "content": """你是一个有帮助的AI助手。请遵循以下准则：
            1. 用中文回答用户的问题
            2. 保持友好和专业
            3. 如果不知道答案，诚实说明
            4. 避免生成有害或不适当的内容"""
        }
        messages.append(system_prompt)
        
        # 添加对话历史（限制最近10轮）
        for msg in conversation_history[-20:]:  # 最多20条消息
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return messages
    
    def chat(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        处理用户输入并返回所有模型的响应
        
        Args:
            user_input: 用户输入文本
            conversation_history: 对话历史
            
        Returns:
            包含所有模型响应的字典
        """
        if conversation_history is None:
            conversation_history = []
        
        # 初始化状态
        initial_state = ChatState(
            user_input=user_input,
            conversation_history=conversation_history,
            model_responses={},
            metadata={
                "request_timestamp": datetime.now().isoformat(),
                "input_length": len(user_input)
            }
        )
        
        try:
            # 执行图
            final_state = self.graph.invoke(initial_state)
            
            # 构建响应
            response = {
                "success": True,
                "user_input": user_input,
                "model_responses": final_state.model_responses,
                "conversation_history": final_state.conversation_history,
                "metadata": final_state.metadata,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"聊天处理完成，生成 {len(final_state.model_responses)} 个模型响应")
            
        except Exception as e:
            logger.error(f"聊天处理失败: {e}")
            response = {
                "success": False,
                "error": str(e),
                "user_input": user_input,
                "model_responses": {},
                "timestamp": datetime.now().isoformat()
            }
        
        return response
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        available = []
        for model_type in ModelType:
            if self.models.get(model_type) is not None:
                available.append(model_type.value)
        return available
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        info = {
            "available_models": self.get_available_models(),
            "total_models": len(ModelType),
            "config": {
                "max_tokens": os.getenv("MAX_TOKENS", 2000),
                "temperature": os.getenv("TEMPERATURE", 0.7),
                "deepseek_model": os.getenv("DEEPSEEK_MODEL"),
                "minimax_model": os.getenv("MINIMAX_MODEL"),
                "qwen_model": os.getenv("QWEN_MODEL")
            }
        }
        return info

# 单例实例
_agent_instance = None

def get_agent() -> MultiModelChatAgent:
    """获取智能体单例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = MultiModelChatAgent()
    return _agent_instance

if __name__ == "__main__":
    # 测试代码
    agent = get_agent()
    
    print("=" * 50)
    print("多模型智能问答客服系统")
    print("=" * 50)
    
    # 显示模型信息
    model_info = agent.get_model_info()
    print(f"可用模型: {model_info['available_models']}")
    print(f"配置: {json.dumps(model_info['config'], indent=2, ensure_ascii=False)}")
    
    # 测试对话
    test_input = "你好，请介绍一下你自己"
    print(f"\n测试输入: {test_input}")
    
    response = agent.chat(test_input)
    
    print(f"\n响应状态: {'成功' if response['success'] else '失败'}")
    
    if response['success']:
        print("\n各模型响应:")
        for model, resp in response['model_responses'].items():
            print(f"\n{model.upper()}:")
            print(f"{resp[:200]}...")
    else:
        print(f"错误: {response['error']}")
    
    print("\n" + "=" * 50)