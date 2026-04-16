# 🐳 Hermes Web Demo - Docker 快速部署指南

## 📋 概述

这是一个完整的 Web 应用 Docker 镜像，包含：
- Flask Web 应用 + API 接口
- 响应式 Web 界面
- 健康检查系统
- 生产就绪配置

## 🚀 快速开始

### 方法1：直接运行（最简单）

```bash
# 拉取并运行镜像（端口映射到 5000）
docker run -d -p 5000:5000 --name hermes-web oijnno/hermes-web-demo:latest

# 查看运行状态
docker ps

# 查看日志
docker logs -f hermes-web

# 测试应用
curl http://localhost:5000/api/health
```

### 方法2：使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  web:
    image: oijnno/hermes-web-demo:latest
    container_name: hermes-web-demo
    ports:
      - "5000:5000"
    environment:
      - PORT=5000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

运行：
```bash
docker-compose up -d
```

### 方法3：从源码构建（自定义）

```bash
# 克隆项目
git clone https://github.com/oijnno/hermes-web-demo.git
cd hermes-web-demo/web-demo

# 构建镜像
docker build -t my-hermes-web-demo:latest .

# 运行
docker run -d -p 5000:5000 --name my-web my-hermes-web-demo:latest
```

## 🌐 访问应用

### 本地访问
- 主页: http://localhost:5000
- 健康检查: http://localhost:5000/api/health
- 系统信息: http://localhost:5000/api/info
- 回显测试: http://localhost:5000/api/echo/hello

### 外网访问（阿里云）
1. **获取公网 IP**
   ```bash
   curl ifconfig.me
   ```

2. **配置安全组**
   - 登录阿里云控制台
   - ECS 实例 → 安全组 → 配置规则
   - 添加入方向规则：
     - 协议: TCP
     - 端口: 5000
     - 授权对象: 0.0.0.0/0

3. **访问地址**
   - http://<你的公网IP>:5000

## 🔧 管理命令

### 容器管理
```bash
# 启动/停止/重启
docker start hermes-web
docker stop hermes-web
docker restart hermes-web

# 查看状态
docker ps
docker ps -a  # 查看所有容器

# 查看日志
docker logs hermes-web
docker logs -f hermes-web  # 实时日志
docker logs --tail=100 hermes-web  # 最后100行

# 进入容器
docker exec -it hermes-web bash
docker exec -it hermes-web sh

# 删除容器
docker rm hermes-web
docker rm -f hermes-web  # 强制删除运行中的容器
```

### 镜像管理
```bash
# 查看镜像
docker images
docker images | grep hermes

# 拉取最新镜像
docker pull oijnno/hermes-web-demo:latest

# 删除镜像
docker rmi oijnno/hermes-web-demo:latest
```

### 资源监控
```bash
# 查看容器资源使用
docker stats hermes-web

# 查看系统资源
docker system df
```

## 📊 应用功能

### Web 界面
- 响应式设计，支持手机/平板/电脑
- 实时显示服务器信息
- 交互式 API 测试

### API 接口
- `GET /` - 主页
- `GET /api/health` - 健康检查（返回 JSON）
- `GET /api/info` - 系统信息（Python 版本、环境变量等）
- `GET /api/echo/<message>` - 消息处理（反转、大写等）

### 健康检查
```bash
# 手动检查
curl http://localhost:5000/api/health

# 预期响应
{
  "status": "healthy",
  "service": "web-demo",
  "version": "1.0.0",
  "hostname": "容器ID"
}
```

## 🛡️ 生产环境配置

### 1. 使用 Nginx 反向代理
```nginx
# nginx.conf 片段
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 配置 SSL（HTTPS）
使用 Let's Encrypt：
```bash
# 安装 certbot
apt install certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com
```

### 3. 资源限制
```yaml
# docker-compose.prod.yml
services:
  web:
    image: oijnno/hermes-web-demo:latest
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

## 🔍 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看占用端口的进程
netstat -tulpn | grep :5000

# 使用其他端口
docker run -d -p 5001:5000 --name hermes-web oijnno/hermes-web-demo:latest
```

#### 2. 容器启动失败
```bash
# 查看详细错误
docker logs hermes-web

# 检查 Docker 服务
systemctl status docker

# 清理 Docker 缓存
docker system prune -a
```

#### 3. 无法从外网访问
- 检查安全组规则
- 检查服务器防火墙
- 测试本地访问：`curl http://localhost:5000`

#### 4. 内存不足
```bash
# 查看内存使用
free -h

# 限制容器内存
docker run -d -p 5000:5000 --memory="512m" --name hermes-web oijnno/hermes-web-demo:latest
```

### 调试命令
```bash
# 检查容器内部
docker exec hermes-web ps aux
docker exec hermes-web netstat -tulpn
docker exec hermes-web cat /etc/os-release

# 检查网络
docker network ls
docker network inspect bridge

# 性能测试
docker stats
docker top hermes-web
```

## 🔄 更新和维护

### 更新镜像
```bash
# 拉取最新版本
docker pull oijnno/hermes-web-demo:latest

# 停止旧容器
docker stop hermes-web
docker rm hermes-web

# 运行新容器
docker run -d -p 5000:5000 --name hermes-web oijnno/hermes-web-demo:latest
```

### 备份数据
```bash
# 备份容器为镜像
docker commit hermes-web hermes-web-backup

# 导出镜像
docker save -o hermes-web-backup.tar hermes-web-backup

# 导入镜像
docker load -i hermes-web-backup.tar
```

### 监控和日志
```bash
# 设置日志轮转
docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 ...

# 查看最近错误
docker logs hermes-web | grep -i error

# 监控访问日志
docker exec hermes-web tail -f /var/log/access.log 2>/dev/null || echo "无访问日志"
```

## 📈 扩展建议

### 添加数据库
```python
# 在 app.py 中添加数据库支持
import sqlite3
# 或
import psycopg2
```

### 添加用户认证
```python
# 使用 Flask-Login
from flask_login import LoginManager, UserMixin, login_user, logout_user
```

### 添加文件上传
```python
# 使用 Flask-Uploads
from flask_uploads import UploadSet, configure_uploads, IMAGES
```

### 添加任务队列
```docker
# 添加 Redis 和 Celery
services:
  redis:
    image: redis:alpine
  celery:
    build: .
    command: celery -A app.celery worker --loglevel=info
```

## 🆘 获取帮助

### 检查应用状态
```bash
# 完整状态检查
./test_app.py http://localhost:5000
```

### 查看文档
- GitHub: https://github.com/oijnno/hermes-web-demo
- Docker Hub: https://hub.docker.com/r/oijnno/hermes-web-demo

### 报告问题
1. 运行 `docker logs hermes-web > error.log`
2. 提供错误日志
3. 描述复现步骤

---

**一键部署完成！** 🎉

**运行命令：**
```bash
docker run -d -p 5000:5000 --name hermes-web oijnno/hermes-web-demo:latest
```

**验证命令：**
```bash
curl http://localhost:5000/api/health
```

**访问地址：** http://localhost:5000