# 智能问答客服系统

基于 Python + Flask + LangGraph 的多模型智能问答客服系统，支持 DeepSeek、MiniMax、Qwen 三种 AI 模型。

## 功能特点

- 🚀 **多模型支持**: 同时集成 DeepSeek、MiniMax、Qwen 三种主流 AI 模型
- 🤖 **智能工作流**: 使用 LangGraph 构建状态图管理对话流程
- 💬 **实时对话**: 支持多轮对话，保持上下文连贯性
- 🎨 **现代化界面**: 响应式设计，支持桌面和移动端
- 🔧 **完整 API**: 提供 RESTful API 接口，便于集成
- 📊 **会话管理**: 支持多用户会话，自动清理过期会话

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web 前端      │    │   Flask 后端    │    │   AI 模型 API   │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   (DeepSeek)    │
│                 │    │                 │    │   (MiniMax)     │
│   • 聊天界面     │    │   • 路由处理    │    │   (Qwen)        │
│   • 模型选择     │    │   • 会话管理    │    └─────────────────┘
│   • 实时更新     │    │   • LangGraph  │
└─────────────────┘    │   • 错误处理    │
                       └─────────────────┘
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd web-demo

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
# 开发模式
python chatbot_app.py

# 或者使用 gunicorn 生产模式
gunicorn -w 4 -b 0.0.0.0:5000 chatbot_app:app
```

### 4. 访问应用

打开浏览器访问: `http://localhost:5000`

## API 密钥配置

### DeepSeek API
1. 访问 [DeepSeek 平台](https://platform.deepseek.com/api_keys)
2. 注册账号并创建 API 密钥
3. 在 `.env` 文件中设置: `DEEPSEEK_API_KEY=your-key`

### MiniMax API
1. 访问 [MiniMax 平台](https://platform.minimaxi.com/)
2. 注册账号并创建 API 密钥
3. 在 `.env` 文件中设置: `MINIMAX_API_KEY=your-key`

### Qwen API
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册账号并创建 API 密钥
3. 在 `.env` 文件中设置: `QWEN_API_KEY=your-key`

## API 接口

### 获取可用模型
```
GET /api/models
```

### 发送消息
```
POST /api/chat
Content-Type: application/json

{
    "model": "deepseek",  // deepseek, minimax, qwen
    "message": "你好，请介绍一下你自己",
    "user_id": "optional-user-id"
}
```

### 获取聊天历史
```
GET /api/history?user_id=<user_id>
```

### 清空历史
```
POST /api/clear
Content-Type: application/json

{
    "user_id": "user-id"
}
```

### 健康检查
```
GET /api/health
```

## Docker 部署

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

### Docker Compose
```bash
docker-compose up -d
```

## 项目结构

```
web-demo/
├── chatbot_app.py          # 主应用文件
├── requirements.txt        # Python 依赖
├── Dockerfile             # Docker 配置
├── .env.example           # 环境变量示例
├── models/                # 模型相关代码
│   ├── model_manager.py   # 模型管理器
│   └── workflow.py        # LangGraph 工作流
├── templates/             # HTML 模板
│   └── chatbot/
│       └── index.html     # 聊天界面
├── static/                # 静态资源
│   ├── css/
│   │   └── chatbot.css    # 样式文件
│   └── js/
│       └── chatbot.js     # JavaScript 文件
└── README.md              # 本文档
```

## 技术栈

- **后端**: Python 3.11, Flask, LangGraph, LangChain
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **AI 模型**: DeepSeek API, MiniMax API, Qwen API
- **部署**: Docker, Gunicorn
- **开发工具**: Git, VS Code

## 开发指南

### 添加新模型
1. 在 `models/model_manager.py` 的 `__init__` 方法中添加模型配置
2. 实现对应的 `call_<modelname>` 方法
3. 更新前端界面显示新模型

### 自定义工作流
1. 修改 `models/workflow.py` 中的工作流节点
2. 可以添加新的处理步骤，如：情感分析、意图识别等

### 样式定制
1. 修改 `static/css/chatbot.css` 中的 CSS 变量
2. 调整颜色、布局等样式

## 故障排除

### 模型不可用
- 检查 API 密钥是否正确配置
- 确认 API 服务是否正常
- 查看控制台错误日志

### 应用无法启动
- 检查 Python 依赖是否安装完整
- 确认端口 5000 是否被占用
- 查看 Flask 启动日志

### 界面显示异常
- 检查静态资源路径是否正确
- 清除浏览器缓存
- 查看浏览器控制台错误

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues
- 项目维护者邮箱