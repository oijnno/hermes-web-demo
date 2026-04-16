#!/usr/bin/env python3
"""
智能问答客服系统 - 基于 Flask + LangGraph
支持 DeepSeek、MiniMax、Qwen 三种模型
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
from datetime import datetime
import eventlet
eventlet.monkey_patch()

# 导入自定义模块
from models.model_manager import ModelManager
from models.workflow import ChatbotWorkflow

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hermes-chatbot-secret-key-2026')
CORS(app)

# 初始化模型管理器和工作流
model_manager = ModelManager()
workflow = ChatbotWorkflow(model_manager)

# 存储用户会话
user_sessions = {}

def get_user_session(user_id=None):
    """获取或创建用户会话"""
    if not user_id:
        user_id = session.get('user_id')
        if not user_id:
            user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            session['user_id'] = user_id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "history": [],
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
    
    # 更新最后活跃时间
    user_sessions[user_id]["last_active"] = datetime.now().isoformat()
    
    return user_id, user_sessions[user_id]

@app.route('/')
def index():
    """主页 - 显示三种模型的聊天界面"""
    user_id, user_session = get_user_session()
    
    available_models = model_manager.get_available_models()
    
    return render_template('chatbot/index.html',
                         user_id=user_id,
                         models=available_models,
                         history=user_session["history"])

@app.route('/chatbot')
def chatbot():
    """聊天机器人页面"""
    return index()

@app.route('/api/models')
def get_models():
    """获取可用模型列表"""
    models = model_manager.get_available_models()
    return jsonify({
        "success": True,
        "models": models,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据不能为空"
            }), 400
        
        model_id = data.get('model', 'deepseek')
        message = data.get('message', '').strip()
        user_id = data.get('user_id')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "消息内容不能为空"
            }), 400
        
        # 获取用户会话
        user_id, user_session = get_user_session(user_id)
        history = user_session["history"]
        
        print(f"用户 {user_id} 使用模型 {model_id} 发送消息: {message[:50]}...")
        
        # 运行工作流
        result = workflow.run(model_id, message, history)
        
        if result["success"]:
            # 更新会话历史
            user_session["history"] = result["history"]
            
            return jsonify({
                "success": True,
                "response": result["response"],
                "model": model_id,
                "user_id": user_id,
                "history": result["history"],
                "timestamp": result["timestamp"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"],
                "model": model_id,
                "user_id": user_id,
                "timestamp": result["timestamp"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取聊天历史"""
    user_id = request.args.get('user_id')
    user_id, user_session = get_user_session(user_id)
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "history": user_session["history"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """清空聊天历史"""
    user_id = request.json.get('user_id') if request.json else None
    user_id, user_session = get_user_session(user_id)
    
    user_session["history"] = []
    
    return jsonify({
        "success": True,
        "message": "聊天历史已清空",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    """健康检查接口"""
    available_models = model_manager.get_available_models()
    active_sessions = len(user_sessions)
    
    return jsonify({
        "status": "healthy",
        "service": "hermes-chatbot",
        "version": "1.0.0",
        "models": available_models,
        "active_sessions": active_sessions,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/info')
def info():
    """系统信息接口"""
    import platform
    import sys
    
    return jsonify({
        "python_version": platform.python_version(),
        "system": platform.system(),
        "platform": platform.platform(),
        "flask_version": "2.3.0",
        "langgraph_version": "0.0.30",
        "current_time": datetime.now().isoformat(),
        "environment": {
            "DEEPSEEK_API_KEY": "已设置" if os.getenv("DEEPSEEK_API_KEY") else "未设置",
            "MINIMAX_API_KEY": "已设置" if os.getenv("MINIMAX_API_KEY") else "未设置",
            "QWEN_API_KEY": "已设置" if os.getenv("QWEN_API_KEY") else "未设置"
        }
    })

# 清理过期会话的定时任务
def cleanup_sessions():
    """清理超过24小时未活动的会话"""
    import threading
    import time
    
    def cleanup():
        while True:
            time.sleep(3600)  # 每小时检查一次
            now = datetime.now()
            expired_users = []
            
            for user_id, session_data in user_sessions.items():
                last_active = datetime.fromisoformat(session_data["last_active"])
                if (now - last_active).total_seconds() > 86400:  # 24小时
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                del user_sessions[user_id]
                print(f"清理过期会话: {user_id}")
    
    thread = threading.Thread(target=cleanup, daemon=True)
    thread.start()

if __name__ == '__main__':
    # 启动会话清理任务
    cleanup_sessions()
    
    # 获取端口
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("智能问答客服系统启动中...")
    print(f"服务地址: http://0.0.0.0:{port}")
    print("=" * 60)
    
    # 显示可用模型
    models = model_manager.get_available_models()
    print("可用模型:")
    for model in models:
        status = "✓ 可用" if model["available"] else "✗ 不可用 (API密钥未设置)"
        print(f"  - {model['name']} ({model['id']}): {status}")
    print("=" * 60)
    
    # 启动应用
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)