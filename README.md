# 🚀 阿里云 Docker 部署完整指南

## 📋 项目概述

这是一个由 **Hermes Agent** 自动创建的 Web 演示应用，部署在阿里云服务器的 Docker 容器中，可以通过外网访问。

## 🏗️ 项目结构

```
web-demo/
├── app.py                 # Flask 主应用
├── requirements.txt       # Python 依赖
├── Dockerfile            # Docker 构建配置
├── docker-compose.yml    # Docker Compose 配置
├── deploy.sh             # 一键部署脚本
├── test_app.py           # 应用测试脚本
├── nginx.conf            # Nginx 生产配置示例
├── templates/            # HTML 模板目录
│   └── index.html       # 主页模板
└── README.md            # 项目说明
```

## 🎯 功能特性

### Web 应用功能
- ✅ 响应式 Web 界面
- ✅ 健康检查 API (`/api/health`)
- ✅ 系统信息 API (`/api/info`)
- ✅ 消息回显 API (`/api/echo/<message>`)
- ✅ 实时主机信息显示

### 部署特性
- ✅ Docker 容器化部署
- ✅ Docker Compose 编排
- ✅ 一键部署脚本
- ✅ 健康检查机制
- ✅ 生产就绪配置

## 🚀 快速开始

### 1. 本地测试（开发环境）

```bash
# 进入项目目录
cd web-demo

# 安装 Python 依赖
pip install -r requirements.txt

# 运行应用
python app.py

# 访问 http://localhost:5000
```

### 2. Docker 本地运行

```bash
# 构建镜像
docker build -t web-demo .

# 运行容器
docker run -d -p 5000:5000 --name web-demo web-demo

# 访问 http://localhost:5000
```

### 3. Docker Compose 运行

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🌐 阿里云服务器部署

### 前提条件
1. 阿里云 ECS 实例（已安装 Docker）
2. 公网 IP 地址
3. 安全组配置权限

### 步骤1：上传项目到服务器

```bash
# 使用 SCP 上传（从本地）
scp -r web-demo/ root@你的服务器IP:/root/

# 或者直接在服务器克隆（如果有 Git）
git clone <你的仓库地址>
cd web-demo
```

### 步骤2：一键部署

```bash
# 进入项目目录
cd web-demo

# 给部署脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

部署脚本会自动：
1. 检查 Docker 和 Docker Compose
2. 构建 Docker 镜像
3. 启动容器服务
4. 显示访问信息

### 步骤3：配置阿里云安全组

**重要：** 必须配置安全组才能从外网访问！

1. **登录阿里云控制台**：https://ecs.console.aliyun.com
2. **进入 ECS 实例** → **安全组** → **配置规则**
3. **添加入方向规则**：
   - 规则方向：入方向
   - 授权策略：允许
   - 协议类型：自定义 TCP
   - 端口范围：5000/5000
   - 授权对象：0.0.0.0/0（允许所有 IP，生产环境建议限制）
4. **保存规则**

### 步骤4：获取访问地址

```bash
# 在服务器上查看公网 IP
curl ifconfig.me
# 或
hostname -I
```

**访问地址：**
- 本地：http://localhost:5000
- 公网：http://你的公网IP:5000

## 🔧 生产环境部署建议

### 1. 使用 Nginx 反向代理

```bash
# 安装 Nginx
sudo apt update
sudo apt install nginx -y

# 复制配置文件
sudo cp nginx.conf /etc/nginx/nginx.conf

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 2. 配置域名和 SSL

1. **购买域名**（阿里云、腾讯云等）
2. **配置 DNS 解析**到你的服务器 IP
3. **申请 SSL 证书**（Let's Encrypt 免费）
4. **更新 Nginx 配置**启用 HTTPS

### 3. 使用 Docker Compose 生产配置

创建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: web-demo-prod
    ports:
      - "127.0.0.1:5000:5000"  # 只允许本地访问
    environment:
      - PORT=5000
      - FLASK_ENV=production
    restart: always
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 📊 监控和维护

### 查看应用状态

```bash
# 查看容器状态
docker ps
docker-compose ps

# 查看应用日志
docker-compose logs -f web
docker logs -f web-demo

# 检查健康状态
curl http://localhost:5000/api/health
```

### 运行测试

```bash
# 运行完整测试
python test_app.py

# 测试特定端点
python test_app.py http://你的公网IP:5000
```

### 更新和重启

```bash
# 更新代码后重新构建
docker-compose build
docker-compose up -d

# 或者使用部署脚本
./deploy.sh
```

## 🔒 安全建议

### 1. 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Docker 安全
```bash
# 使用非 root 用户运行容器
# 已在 Dockerfile 中配置

# 定期更新镜像
docker-compose pull
docker-compose up -d
```

### 3. 应用安全
- 不要在生产环境使用 `debug=True`
- 配置适当的 CORS 策略
- 限制请求频率
- 记录访问日志

## 🐛 故障排除

### 常见问题

#### 1. 无法从外网访问
- 检查安全组规则
- 检查服务器防火墙
- 确认容器正在运行：`docker ps`
- 测试本地访问：`curl http://localhost:5000`

#### 2. 端口被占用
```bash
# 查看占用端口的进程
sudo netstat -tulpn | grep :5000

# 停止占用进程或修改应用端口
```

#### 3. Docker 构建失败
```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

#### 4. 应用启动失败
```bash
# 查看详细日志
docker-compose logs --tail=100 web

# 进入容器调试
docker exec -it web-demo bash
```

### 调试命令

```bash
# 检查网络连接
ping 你的公网IP
telnet 你的公网IP 5000

# 检查服务状态
systemctl status docker
systemctl status nginx

# 查看系统资源
top
df -h
free -h
```

## 📈 性能优化

### 1. Docker 优化
```bash
# 限制容器资源
docker run -d --memory="512m" --cpus="0.5" ...

# 使用多阶段构建减小镜像大小
```

### 2. Flask 优化
```python
# 生产环境配置
app.config['DEBUG'] = False
app.config['TESTING'] = False

# 使用 Gunicorn 多 worker
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### 3. 数据库连接池（如果需要）
```python
# 使用连接池管理数据库连接
from DBUtils.PooledDB import PooledDB
```

## 🔄 自动化部署

### GitHub Actions 示例

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Aliyun

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Aliyun
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.ALIYUN_HOST }}
          username: ${{ secrets.ALIYUN_USERNAME }}
          key: ${{ secrets.ALIYUN_SSH_KEY }}
          script: |
            cd /root/web-demo
            git pull
            ./deploy.sh
```

## 📚 相关资源

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Docker 官方文档](https://docs.docker.com/)
- [阿里云 ECS 文档](https://help.aliyun.com/product/25365.html)
- [Nginx 配置指南](https://nginx.org/en/docs/)

## 🆘 获取帮助

如果遇到问题：

1. **查看日志**：`docker-compose logs -f`
2. **运行测试**：`python test_app.py`
3. **检查状态**：`docker ps`、`curl http://localhost:5000/api/health`
4. **联系支持**：提供错误日志和部署环境信息

---

**部署完成！** 🎉 现在你的 Web 应用应该可以通过外网访问了。

**访问地址：** http://你的公网IP:5000

**下一步建议：**
1. 配置域名和 SSL 证书
2. 设置监控和告警
3. 配置自动化部署
4. 添加数据库支持（如需要）
