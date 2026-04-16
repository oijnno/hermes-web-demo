"""
LangGraph 工作流服务 - 智能问答流程管理
"""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import operator
from datetime import datetime

from src.services.model_service import model_service
from src.core.logging import setup_logging

logger = setup_logging()

class WorkflowState(TypedDict):
    """工作流状态"""
    messages: Annotated[List[Dict[str, Any]], add_messages]
    model_id: str
    user_query: str
    response: str
    history: List[Dict[str, Any]]
    timestamp: str
    error: Optional[str]

class ChatbotWorkflow:
    """智能问答工作流"""
    
    def __init__(self):
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """构建 LangGraph 工作流"""
        
        # 创建状态图
        workflow = StateGraph(WorkflowState)
        
        # 添加节点
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("preprocess_query", self._preprocess_query)
        workflow.add_node("check_safety", self._check_safety)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("postprocess_response", self._postprocess_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # 添加边
        workflow.set_entry_point("validate_input")
        
        # 正常流程
        workflow.add_edge("validate_input", "preprocess_query")
        workflow.add_edge("preprocess_query", "check_safety")
        workflow.add_edge("check_safety", "generate_response")
        workflow.add_edge("generate_response", "postprocess_response")
        workflow.add_edge("postprocess_response", END)
        
        # 错误处理
        workflow.add_edge("validate_input", "handle_error", "error")
        workflow.add_edge("preprocess_query", "handle_error", "error")
        workflow.add_edge("check_safety", "handle_error", "error")
        workflow.add_edge("generate_response", "handle_error", "error")
        workflow.add_edge("postprocess_response", "handle_error", "error")
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def _validate_input(self, state: WorkflowState) -> WorkflowState:
        """验证输入"""
        logger.info(f"验证输入: {state['model_id']} - {state['user_query'][:50]}...")
        
        # 检查查询是否为空
        if not state['user_query'] or len(state['user_query'].strip()) == 0:
            state['error'] = "查询内容不能为空"
            return state
        
        # 检查模型是否支持
        if state['model_id'] not in ['deepseek', 'minimax', 'qwen']:
            state['error'] = f"不支持的模型: {state['model_id']}"
            return state
        
        # 检查查询长度
        if len(state['user_query']) > 2000:
            state['error'] = "查询内容过长，请控制在2000字符以内"
            return state
        
        return state
    
    def _preprocess_query(self, state: WorkflowState) -> WorkflowState:
        """预处理查询"""
        logger.info("预处理查询")
        
        query = state['user_query'].strip()
        
        # 简单的查询增强
        if len(query) < 10:
            query = f"请详细回答: {query}"
        
        # 添加上下文提示（根据模型特性）
        if state['model_id'] == 'deepseek':
            query = f"[技术问题] {query}"
        elif state['model_id'] == 'minimax':
            query = f"[创意对话] {query}"
        elif state['model_id'] == 'qwen':
            query = f"[中文对话] {query}"
        
        state['user_query'] = query
        return state
    
    def _check_safety(self, state: WorkflowState) -> WorkflowState:
        """安全检查"""
        logger.info("进行安全检查")
        
        # 简单的敏感词检查
        sensitive_keywords = [
            "暴力", "色情", "赌博", "毒品", "诈骗",
            "自杀", "自残", "仇恨", "歧视", "极端"
        ]
        
        query_lower = state['user_query'].lower()
        for keyword in sensitive_keywords:
            if keyword in query_lower:
                state['error'] = f"查询包含敏感内容: {keyword}"
                return state
        
        return state
    
    async def _generate_response(self, state: WorkflowState) -> WorkflowState:
        """生成响应"""
        logger.info(f"使用模型 {state['model_id']} 生成响应")
        
        try:
            # 调用模型服务
            result = await model_service.call_model(
                state['model_id'],
                state['user_query'],
                state.get('history', [])
            )
            
            if 'error' in result:
                state['error'] = result['error']
                return state
            
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
                "timestamp": datetime.now().isoformat(),
                "tokens": result.get('tokens')
            })
            
            # 限制历史记录长度
            if len(history) > 20:
                history = history[-20:]
            
            state['history'] = history
            
        except Exception as e:
            logger.error(f"生成响应失败: {e}")
            state['error'] = f"生成响应时发生错误: {str(e)}"
        
        return state
    
    def _postprocess_response(self, state: WorkflowState) -> WorkflowState:
        """后处理响应"""
        logger.info("后处理响应")
        
        # 添加时间戳
        state['timestamp'] = datetime.now().isoformat()
        
        # 清理响应中的多余空白
        if state.get('response'):
            state['response'] = state['response'].strip()
        
        return state
    
    def _handle_error(self, state: WorkflowState) -> WorkflowState:
        """错误处理"""
        error_msg = state.get('error', '未知错误')
        logger.error(f"工作流错误: {error_msg}")
        
        # 生成友好的错误响应
        state['response'] = f"抱歉，处理您的请求时出现错误：{error_msg}\n\n请稍后重试或联系管理员。"
        state['timestamp'] = datetime.now().isoformat()
        
        return state
    
    async def run(
        self,
        model_id: str,
        query: str,
        history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """运行工作流"""
        
        try:
            # 初始化状态
            initial_state = {
                "messages": [],
                "model_id": model_id,
                "user_query": query,
                "response": "",
                "history": history or [],
                "timestamp": "",
                "error": None
            }
            
            # 执行工作流
            result = self.workflow.invoke(initial_state)
            
            if result.get('error'):
                return {
                    "success": False,
                    "error": result['error'],
                    "model": model_id,
                    "timestamp": result['timestamp']
                }
            
            return {
                "success": True,
                "response": result['response'],
                "model": model_id,
                "history": result['history'],
                "timestamp": result['timestamp']
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            return {
                "success": False,
                "error": f"工作流执行失败: {str(e)}",
                "model": model_id,
                "timestamp": datetime.now().isoformat()
            }

# 创建全局工作流实例
chatbot_workflow = ChatbotWorkflow()