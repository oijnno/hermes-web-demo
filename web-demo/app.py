#!/usr/bin/env python3
"""
Web Demo - 简单的 Flask Web 应用
可以通过外网访问的演示应用
"""

from flask import Flask, render_template, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def index():
    """主页"""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    return render_template('index.html', 
                         hostname=hostname,
                         ip_address=ip_address,
                         message="欢迎访问 Hermes Agent 创建的 Web 应用！")

@app.route('/api/health')
def health():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "web-demo",
        "version": "1.0.0",
        "hostname": socket.gethostname()
    })

@app.route('/api/info')
def info():
    """系统信息接口"""
    import platform
    import datetime
    
    return jsonify({
        "python_version": platform.python_version(),
        "system": platform.system(),
        "platform": platform.platform(),
        "current_time": datetime.datetime.now().isoformat(),
        "environment": dict(os.environ)
    })

@app.route('/api/echo/<message>')
def echo(message):
    """回显接口"""
    return jsonify({
        "original": message,
        "reversed": message[::-1],
        "uppercase": message.upper(),
        "length": len(message)
    })

if __name__ == '__main__':
    # 获取端口，默认为 5000
    port = int(os.environ.get('PORT', 5000))
    
    # 监听所有网络接口，允许外网访问
    app.run(host='0.0.0.0', port=port, debug=True)