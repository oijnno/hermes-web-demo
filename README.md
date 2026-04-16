# Hermes 智能问答客服系统

基于 **FastAPI + LangGraph** 的多模型智能问答客服系统，支持 **DeepSeek、MiniMax、Qwen** 三种 AI 模型。

## ✨ 功能特点

- 🚀 **多模型支持**: 同时集成 DeepSeek、MiniMax、Qwen 三种主流 AI 模型
- ⚡ **高性能**: 基于 FastAPI 的异步架构，支持高并发
- 🤖 **智能工作流**: 使用 LangGraph 构建状态图管理对话流程
- 💬 **实时对话**: 支持多轮对话，保持上下文连贯性
- 🎨 **现代化界面**: 响应式设计，支持桌面和移动端
- 🔧 **完整 API**: 提供 RESTful API 接口，便于集成
- 📊 **会话管理**: 支持多用户会话，自动清理过期会话
- 🗄️ **数据持久化**: SQLite 数据库存储聊天历史
- 🐳 **容器化部署**: 支持 Docker 和 Docker Compose

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web 前端       │    │   FastAPI 后端   │    │   AI 模型 API   │
│   (HTML/CSS/JS)  │◄──►│   (Python)       │◄──►│   (DeepSeek)    │
│                  │    │                  │    │   (MiniMax)     │
│   • 聊天界面      │    │   • 异步路由      │    │   (Qwen)        │
│   • 模型选择      │    │   • 会话管理      │    └─────────────────┘
│   • 实时更新      │    │   • LangGraph   │
└─────────────────┘    │   • 数据库操作    │
                       │   • 错误处理      │
                       └─────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/oijnno/hermes-web-demo.git
cd hermes-web-demo

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，配置 API 密钥
# 至少配置一个模型的 API 密钥
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
# 使用启动脚本（推荐）
./start.sh

# 或手动启动
uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload
```

### 4. 访问应用

打开浏览器访问: `http://localhost:5000`

## 🔑 API 密钥配置

### DeepSeek API
1. 访问 [DeepSeek 平台](https://platform.deepseek.com/api_keys)
2. 注册账号并创建 API 密钥
3. 在 `.env` 文件中设置: `DEEPSEEK_API_KEY=your_key_here`

### MiniMax API
1. 访问 [MiniMax 平台](https://platform.minimaxi.com/)
2. 注册账号并创建 API 密钥
3. 在 `.env` 文件中设置: `MINIMAX_API_KEY=your_key_here`

### Qwen API
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册账号并创建 API 密钥
3. 在 `.env` 文件中设置: `QWEN_API_KEY=your_key_here`

## 📡 API 接口

### 健康检查
```
GET /api/v1/chat/health
```

### 获取可用模型
```
GET /api/v1/chat/models
```

### 发送消息
```
POST /api/v1/chat/chat
Content-Type: application/json

{
    "model": "deepseek",  // deepseek, minimax, qwen
    "message": "你好，请介绍一下你自己",
    "session_id": "optional-session-id",
    "stream": false
}
```

### 获取聊天历史
```
GET /api/v1/chat/history/{session_id}?limit=20&offset=0
```

### 清空历史
```
POST /api/v1/chat/clear/{session_id}
```

### 获取会话信息
```
GET /api/v1/chat/session/{session_id}
```

## 🐳 Docker 部署

### 构建镜像
```bash
docker build -t hermes-chatbot .
```

### 运行容器
```bash
docker run -d \
  -p 5000:5000 \
  --name hermes-chatbot \
  --env-file .env \
  hermes-chatbot
```

### Docker Compose（推荐）
```bash
docker-compose up -d
```

## 📁 项目结构

```
hermes-web-demo/
├── src/                    # 源代码目录
│   ├── api/               # API 路由层
│   │   ├── api_v1/        # API v1 版本
│   │   └── routes/        # 路由定义
│   ├── core/              # 核心配置
│   │   ├── config.py      # 应用配置
│   │   ├── logging.py     # 日志配置
│   │   └── middleware.py  # 中间件
│   ├── database/          # 数据库
│   │   └── session.py     # 数据库会话
│   ├── models/            # 数据模型
│   │   └── db_models.py   # SQLAlchemy 模型
│   ├── schemas/           # Pydantic 模式
│   │   └── chat_schemas.py # 聊天相关模式
│   ├── services/          # 业务服务
│   │   ├── model_service.py    # 模型服务
│   │   ├── session_service.py  # 会话服务
│   │   └── workflow_service.py # LangGraph 工作流
│   ├── static/            # 静态文件
│   │   ├── css/           # CSS 样式
│   │   └── js/            # JavaScript
│   ├── templates/         # 模板文件
│   │   ├── chatbot/       # 聊天模板
│   │   └── index.html     # 首页
│   └── main.py           # FastAPI 主应用
├── tests/                 # 测试目录
├── alembic/              # 数据库迁移
├── docs/                 # 文档
├── scripts/              # 脚本
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # Docker Compose 配置
├── .env.example         # 环境变量示例
├── start.sh             # 启动脚本
└── README.md            # 本文档
```

## 🛠️ 技术栈

- **后端**: Python 3.11, FastAPI, Uvicorn, LangGraph
- **数据库**: SQLAlchemy, SQLite
- **数据验证**: Pydantic
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **AI 模型**: DeepSeek API, MiniMax API, Qwen API
- **部署**: Docker, Docker Compose, Nginx
- **开发工具**: Git, VS Code

## 🔧 开发指南

### 添加新模型
1. 在 `src/services/model_service.py` 的 `__init__` 方法中添加模型配置
2. 在 `src/core/config.py` 中添加对应的配置项
3. 更新前端界面显示新模型

### 自定义工作流
1. 修改 `src/services/workflow_service.py` 中的工作流节点
2. 可以添加新的处理步骤，如：情感分析、意图识别等

### 样式定制
1. 修改 `src/static/css/chatbot.css` 中的 CSS 变量
2. 调整颜色、布局等样式

### 数据库迁移
```bash
# 初始化 Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head
```

## 🐛 故障排除

### 模型不可用
- 检查 API 密钥是否正确配置
- 确认 API 服务是否正常
- 查看控制台错误日志

### 应用无法启动
- 检查 Python 依赖是否安装完整
- 确认端口 5000 是否被占用
- 查看 FastAPI 启动日志

### 界面显示异常
- 检查静态资源路径是否正确
- 清除浏览器缓存
- 查看浏览器控制台错误

### 数据库问题
- 确认数据库文件权限
- 检查数据库连接配置
- 查看 SQLAlchemy 日志

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues: [https://github.com/oijnno/hermes-web-demo/issues](https://github.com/oijnno/hermes-web-demo/issues)
- 项目维护者邮箱: [请查看 GitHub 项目页面]

## 🔄 更新日志

### v1.0.0 (2024-04-16)
- ✅ 从 Flask 迁移到 FastAPI
- ✅ 完整的异步架构
- ✅ 数据库持久化支持
- ✅ 模块化项目结构
- ✅ Docker Compose 部署支持
- ✅ 完整的 API 文档