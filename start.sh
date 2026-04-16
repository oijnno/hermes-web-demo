#!/bin/bash
# 启动脚本

set -e

echo "🚀 启动 Hermes 智能问答客服系统..."

# 检查 Python 版本
python_version=$(python3 --version | cut -d' ' -f2)
echo "Python 版本: $python_version"

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "❌ 找不到 requirements.txt 文件"
    exit 1
fi

# 安装依赖
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "⚠️  找不到 .env 文件，使用 .env.example 作为模板"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已创建 .env 文件，请编辑该文件配置 API 密钥"
    else
        echo "❌ 找不到 .env.example 文件"
        exit 1
    fi
fi

# 创建必要的目录
mkdir -p logs

# 启动应用
echo "🌐 启动 FastAPI 应用..."
uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 5000 \
    --reload \
    --log-level info

# 如果上面的命令失败，尝试直接运行
if [ $? -ne 0 ]; then
    echo "⚠️  Uvicorn 启动失败，尝试直接运行..."
    python3 -m src.main
fi