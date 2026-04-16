#!/usr/bin/env python3
"""
LangGraph 工作流 - 智能问答客服系统
"""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import operator
from datetime import datetime

class State(TypedDict):
    """工作流状态"""
    messages: Annotated[List[Dict[str, Any]], add_messages]
    model_id: str
    user_query: str
    response: str
    history: List[Dict[str, Any]]
    timestamp: str

class ChatbotWorkflow:
    """智能问答客服工作流"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.workflow = self.build_workflow()
    
    def build_workflow(self):
        """构建 LangGraph 工作流"""
        
        # 创建状态图
        workflow = StateGraph(State)
        
        # 添加节点
        workflow.add_node("validate_input", self.validate_input)
        workflow.add_node("process_query", self.process_query)
        workflow.add_node("generate_response", self.generate_response)
        workflow.add_node("format_output", self.format_output)
        
        # 添加边
        workflow.set_entry_point("validate_input")
        workflow.add_edge("validate_input", "process_query")
        workflow.add_edge("process_query", "generate_response")
        workflow.add_edge("generate_response", "format_output")
        workflow.add_edge("format_output", END)
        
        return workflow.compile()
    
    def validate_input(self, state: State) -> State:
        """验证输入"""
        print(f"验证输入: {state['user_query']}")
        
        if not state['user_query'] or len(state['user_query'].strip()) == 0:
            raise ValueError("查询内容不能为空")
        
        if state['model_id'] not in ['deepseek', 'minimax', 'qwen']:
            raise ValueError(f"不支持的模型: {state['model_id']}")
        
        return state
    
    def process_query(self, state: State) -> State:
        """处理查询"""
        print(f"处理查询: {state['user_query']}")
        
        # 这里可以添加查询预处理逻辑
        # 例如：敏感词过滤、意图识别等
        
        # 简单的查询增强
        enhanced_query = state['user_query']
        if len(enhanced_query) < 10:
            enhanced_query = f"请详细回答: {enhanced_query}"
        
        state['user_query'] = enhanced_query
        return state
    
    def generate_response(self, state: State) -> State:
        """生成响应"""
        print(f"使用模型 {state['model_id']} 生成响应")
        
        # 调用模型管理器
        result = self.model_manager.call_model(
            state['model_id'],
            state['user_query'],
            state.get('history', [])
        )
        
        if 'error' in result:
            state['response'] = f"抱歉，{state['model_id']} 模型暂时不可用: {result['error']}"
        else:
            state['response'] = result['content']
        
        # 更新历史记录
        history = state.get('history', [])
        history.append({
            "role": "user",
            "content": state['user_query'],
            "timestamp": datetime.now().isoformat()
        })
        history.append({
            "role": "assistant",
            "content": state['response'],
            "model": state['model_id'],
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(history) > 20:
            history = history[-20:]
        
        state['history'] = history
        return state
    
    def format_output(self, state: State) -> State:
        """格式化输出"""
        print("格式化输出")
        
        # 添加时间戳
        state['timestamp'] = datetime.now().isoformat()
        
        return state
    
    def run(self, model_id: str, query: str, history: list = None) -> Dict[str, Any]:
        """运行工作流"""
        try:
            # 初始化状态
            initial_state = {
                "messages": [],
                "model_id": model_id,
                "user_query": query,
                "response": "",
                "history": history or [],
                "timestamp": ""
            }
            
            # 执行工作流
            result = self.workflow.invoke(initial_state)
            
            return {
                "success": True,
                "response": result['response'],
                "model": model_id,
                "history": result['history'],
                "timestamp": result['timestamp']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_id,
                "timestamp": datetime.now().isoformat()
            }