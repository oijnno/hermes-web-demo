#!/usr/bin/env python3
"""
AI 客服 Web 应用
展示 DeepSeek、MiniMax、千问三个模型的对话窗口
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv

from agent import get_agent

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# 启用 CORS
CORS(app)

# 初始化智能体
agent = get_agent()

# 会话存储（简单内存存储，生产环境用 Redis）
conversations = {}

def get_conversation(session_id: str):
    """获取或创建会话"""
    if session_id not in conversations:
        conversations[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "model_responses": {}
        }
    return conversations[session_id]

def save_message(session_id: str, role: str, content: str, model: str = None):
    """保存消息到会话"""
    conv = get_conversation(session_id)
    message = {
        "id": str(uuid.uuid4()),
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "model": model
    }
    conv["messages"].append(message)
    conv["updated_at"] = datetime.now().isoformat()
    return message

@app.route('/')
def index():
    """主页 - 显示三个模型的对话窗口"""
    # 生成或获取会话ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # 获取模型信息
    model_info = agent.get_model_info()
    
    return render_template('index.html',
                         session_id=session['session_id'],
                         model_info=model_info)

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        session_id = data.get('session_id', session.get('session_id'))
        
        if not user_input:
            return jsonify({
                "success": False,
                "error": "消息不能为空"
            }), 400
        
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # 获取当前会话历史
        conv = get_conversation(session_id)
        conversation_history = []
        for msg in conv["messages"]:
            conversation_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # 保存用户消息
        save_message(session_id, "user", user_input)
        
        # 调用智能体处理
        response = agent.chat(user_input, conversation_history)
        
        if response["success"]:
            # 保存所有模型的响应
            for model, content in response["model_responses"].items():
                if content and content != "模型不可用" and not content.startswith("调用失败"):
                    save_message(session_id, "assistant", content, model)
            
            # 更新会话中的模型响应
            conv["model_responses"] = response["model_responses"]
            
            return jsonify({
                "success": True,
                "session_id": session_id,
                "responses": response["model_responses"],
                "conversation_id": conv["id"],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": response.get("error", "未知错误"),
                "session_id": session_id
            }), 500
            
    except Exception as e:
        app.logger.error(f"聊天处理错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/conversation/<session_id>', methods=['GET'])
def get_conversation_history(session_id):
    """获取会话历史"""
    try:
        conv = get_conversation(session_id)
        
        # 格式化消息用于前端显示
        formatted_messages = []
        for msg in conv["messages"]:
            formatted_msg = {
                "id": msg["id"],
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"],
                "isUser": msg["role"] == "user"
            }
            if msg.get("model"):
                formatted_msg["model"] = msg["model"]
            formatted_messages.append(formatted_msg)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "conversation": {
                "id": conv["id"],
                "created_at": conv["created_at"],
                "updated_at": conv.get("updated_at", conv["created_at"]),
                "message_count": len(conv["messages"]),
                "messages": formatted_messages
            }
        })
        
    except Exception as e:
        app.logger.error(f"获取会话历史错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/conversation/<session_id>', methods=['DELETE'])
def clear_conversation(session_id):
    """清空会话"""
    try:
        if session_id in conversations:
            # 保留会话ID，只清空消息
            conversations[session_id]["messages"] = []
            conversations[session_id]["model_responses"] = {}
            conversations[session_id]["updated_at"] = datetime.now().isoformat()
            
            return jsonify({
                "success": True,
                "message": "会话已清空",
                "session_id": session_id
            })
        else:
            return jsonify({
                "success": False,
                "error": "会话不存在"
            }), 404
            
    except Exception as e:
        app.logger.error(f"清空会话错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取模型信息"""
    try:
        model_info = agent.get_model_info()
        return jsonify({
            "success": True,
            "models": model_info
        })
    except Exception as e:
        app.logger.error(f"获取模型信息错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        model_info = agent.get_model_info()
        available_models = len(model_info["available_models"])
        
        return jsonify({
            "status": "healthy",
            "service": "ai-chatbot",
            "available_models": available_models,
            "total_models": model_info["total_models"],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息（不包含敏感信息）"""
    config = {
        "max_tokens": os.getenv("MAX_TOKENS", 2000),
        "temperature": os.getenv("TEMPERATURE", 0.7),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "session_ttl": os.getenv("SESSION_TTL", 3600)
    }
    return jsonify({
        "success": True,
        "config": config
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "资源未找到"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"服务器内部错误: {error}")
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500

if __name__ == '__main__':
    # 显示启动信息
    print("=" * 60)
    print("🤖 AI 客服系统启动中...")
    print("=" * 60)
    
    model_info = agent.get_model_info()
    print(f"📊 模型信息:")
    print(f"   可用模型: {', '.join(model_info['available_models'])}")
    print(f"   总模型数: {model_info['total_models']}")
    print(f"   温度设置: {model_info['config']['temperature']}")
    print(f"   最大令牌: {model_info['config']['max_tokens']}")
    
    print(f"\n🌐 Web 服务:")
    port = int(os.getenv('PORT', 5001))
    print(f"   访问地址: http://localhost:{port}")
    print(f"   API 文档: http://localhost:{port}/api")
    print(f"   健康检查: http://localhost:{port}/api/health")
    
    print("\n" + "=" * 60)
    
    # 启动应用
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )