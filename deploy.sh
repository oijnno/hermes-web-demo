#!/bin/bash

# Web Demo 一键部署脚本
# 适用于阿里云服务器 Docker 部署

set -e  # 遇到错误立即退出

echo "🚀 开始部署 Web Demo 应用..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    print_info "Docker 已安装: $(docker --version)"
}

# 检查 Docker Compose 是否安装
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose 未安装，尝试安装..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    print_info "Docker Compose 已安装: $(docker-compose --version)"
}

# 获取公网 IP
get_public_ip() {
    if command -v curl &> /dev/null; then
        PUBLIC_IP=$(curl -s ifconfig.me)
    elif command -v wget &> /dev/null; then
        PUBLIC_IP=$(wget -qO- ifconfig.me)
    else
        PUBLIC_IP="无法获取"
    fi
    echo "$PUBLIC_IP"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if netstat -tuln | grep ":$port " > /dev/null; then
        print_warning "端口 $port 已被占用"
        return 1
    fi
    return 0
}

# 构建 Docker 镜像
build_image() {
    print_info "开始构建 Docker 镜像..."
    docker build -t web-demo:latest .
    
    if [ $? -eq 0 ]; then
        print_info "Docker 镜像构建成功"
    else
        print_error "Docker 镜像构建失败"
        exit 1
    fi
}

# 使用 Docker Compose 启动服务
start_with_compose() {
    print_info "使用 Docker Compose 启动服务..."
    
    # 停止并移除旧容器
    docker-compose down 2>/dev/null || true
    
    # 启动新容器
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_info "服务启动成功"
    else
        print_error "服务启动失败"
        exit 1
    fi
}

# 使用 Docker 直接运行
start_with_docker() {
    print_info "使用 Docker 直接运行..."
    
    # 停止并移除旧容器
    docker stop web-demo 2>/dev/null || true
    docker rm web-demo 2>/dev/null || true
    
    # 运行新容器
    docker run -d \
        --name web-demo \
        -p 5000:5000 \
        --restart unless-stopped \
        web-demo:latest
    
    if [ $? -eq 0 ]; then
        print_info "容器启动成功"
    else
        print_error "容器启动失败"
        exit 1
    fi
}

# 检查服务状态
check_service_status() {
    print_info "检查服务状态..."
    
    # 等待服务启动
    sleep 5
    
    # 检查容器状态
    if docker ps | grep -q "web-demo"; then
        print_info "容器运行正常"
    else
        print_error "容器未运行"
        exit 1
    fi
    
    # 检查应用健康状态
    if curl -s http://localhost:5000/api/health | grep -q "healthy"; then
        print_info "应用健康检查通过"
    else
        print_warning "应用健康检查失败，但容器仍在运行"
    fi
}

# 显示访问信息
show_access_info() {
    PUBLIC_IP=$(get_public_ip)
    
    echo ""
    echo "=========================================="
    echo "🎉 部署完成！"
    echo "=========================================="
    echo ""
    echo "📱 访问地址:"
    echo "   本地: http://localhost:5000"
    if [ "$PUBLIC_IP" != "无法获取" ]; then
        echo "   公网: http://$PUBLIC_IP:5000"
    else
        echo "   公网: 无法获取公网 IP，请手动检查"
    fi
    echo ""
    echo "🔧 API 接口:"
    echo "   健康检查: http://localhost:5000/api/health"
    echo "   系统信息: http://localhost:5000/api/info"
    echo "   回显测试: http://localhost:5000/api/echo/hello"
    echo ""
    echo "📊 管理命令:"
    echo "   查看日志: docker-compose logs -f"
    echo "   停止服务: docker-compose down"
    echo "   重启服务: docker-compose restart"
    echo ""
    echo "⚠️  重要提示:"
    echo "   1. 确保阿里云安全组已开放 5000 端口"
    echo "   2. 生产环境建议配置 Nginx 反向代理和 SSL"
    echo "   3. 定期查看应用日志"
    echo "=========================================="
}

# 配置阿里云安全组提示
show_security_group_info() {
    echo ""
    echo "🔐 阿里云安全组配置指南:"
    echo "   1. 登录阿里云控制台 (https://ecs.console.aliyun.com)"
    echo "   2. 进入你的 ECS 实例"
    echo "   3. 点击 '安全组' 标签"
    echo "   4. 点击 '配置规则'"
    echo "   5. 添加安全组规则:"
    echo "      - 规则方向: 入方向"
    echo "      - 授权策略: 允许"
    echo "      - 协议类型: 自定义 TCP"
    echo "      - 端口范围: 5000/5000"
    echo "      - 授权对象: 0.0.0.0/0 (或你的特定 IP)"
    echo "   6. 点击 '保存'"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "    Web Demo 应用部署脚本"
    echo "=========================================="
    echo ""
    
    # 检查前置条件
    check_docker
    check_docker_compose
    
    # 检查端口
    if ! check_port 5000; then
        print_warning "建议使用其他端口或停止占用端口的服务"
        read -p "是否继续？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 构建镜像
    build_image
    
    # 选择启动方式
    echo ""
    echo "请选择启动方式:"
    echo "1) 使用 Docker Compose (推荐)"
    echo "2) 使用 Docker 直接运行"
    read -p "请输入选择 (1/2): " choice
    
    case $choice in
        1)
            start_with_compose
            ;;
        2)
            start_with_docker
            ;;
        *)
            print_error "无效选择，使用默认方式 (Docker Compose)"
            start_with_compose
            ;;
    esac
    
    # 检查服务状态
    check_service_status
    
    # 显示访问信息
    show_access_info
    
    # 显示安全组配置提示
    show_security_group_info
    
    print_info "部署脚本执行完成！"
}

# 执行主函数
main "$@"