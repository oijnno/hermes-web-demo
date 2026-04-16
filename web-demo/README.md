# Web Demo - Docker 部署配置

## 项目说明
这是一个由 Hermes Agent 自动创建的 Web 演示应用，可以通过外网访问。

## 文件结构
```
web-demo/
├── app.py              # Flask 主应用
├── requirements.txt    # Python 依赖
├── Dockerfile         # Docker 构建文件
├── docker-compose.yml # Docker Compose 配置
├── templates/         # HTML 模板
│   └── index.html    # 主页模板
└── README.md         # 项目说明
```

## 本地运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
# 访问 http://localhost:5000
```

## Docker 运行
```bash
# 构建镜像
docker build -t web-demo .

# 运行容器
docker run -d -p 5000:5000 --name web-demo web-demo
# 访问 http://localhost:5000
```

## Docker Compose 运行
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 外网访问配置

### 1. 阿里云安全组配置
1. 登录阿里云控制台
2. 进入 ECS 实例
3. 配置安全组规则：
   - 协议类型：自定义 TCP
   - 端口范围：5000（或你设置的端口）
   - 授权对象：0.0.0.0/0（允许所有 IP）

### 2. 获取公网 IP
```bash
# 查看公网 IP
curl ifconfig.me
# 或
hostname -I
```

### 3. 访问地址
- 公网 IP: http://<你的公网IP>:5000
- 如果配置了域名: http://<你的域名>:5000

## API 接口
- `GET /` - 主页
- `GET /api/health` - 健康检查
- `GET /api/info` - 系统信息
- `GET /api/echo/<message>` - 回显消息

## 部署脚本
查看 `deploy.sh` 获取一键部署脚本。

## 注意事项
1. 生产环境请使用 Gunicorn 或 Nginx 反向代理
2. 建议配置 SSL/TLS 证书
3. 设置适当的防火墙规则
4. 监控应用日志和性能