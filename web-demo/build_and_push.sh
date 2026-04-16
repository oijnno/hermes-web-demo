#!/bin/bash

# Docker 镜像构建和推送脚本
# 使用方法: ./build_and_push.sh [DOCKERHUB_USERNAME]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
        print_info "安装命令: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
        exit 1
    fi
    print_info "Docker 已安装: $(docker --version)"
}

# 检查是否登录 Docker Hub
check_docker_login() {
    if ! docker info 2>/dev/null | grep -q "Username"; then
        print_warning "未检测到 Docker Hub 登录"
        print_info "请先登录: docker login"
        print_info "或使用: docker login -u YOUR_USERNAME"
        return 1
    fi
    return 0
}

# 构建镜像
build_image() {
    local image_name=$1
    local tag=$2
    
    print_info "开始构建 Docker 镜像: ${image_name}:${tag}"
    
    # 构建镜像
    docker build -t ${image_name}:${tag} .
    
    if [ $? -eq 0 ]; then
        print_info "✅ 镜像构建成功: ${image_name}:${tag}"
        
        # 显示镜像信息
        docker images | grep ${image_name}
    else
        print_error "❌ 镜像构建失败"
        exit 1
    fi
}

# 推送镜像到 Docker Hub
push_image() {
    local image_name=$1
    local tag=$2
    
    print_info "开始推送镜像到 Docker Hub: ${image_name}:${tag}"
    
    # 推送镜像
    docker push ${image_name}:${tag}
    
    if [ $? -eq 0 ]; then
        print_info "✅ 镜像推送成功: ${image_name}:${tag}"
    else
        print_error "❌ 镜像推送失败"
        print_info "请检查:"
        print_info "  1. 是否已登录 Docker Hub: docker login"
        print_info "  2. 是否有推送权限"
        exit 1
    fi
}

# 测试镜像
test_image() {
    local image_name=$1
    local tag=$2
    
    print_info "测试镜像: ${image_name}:${tag}"
    
    # 停止并删除旧容器
    docker stop hermes-web-test 2>/dev/null || true
    docker rm hermes-web-test 2>/dev/null || true
    
    # 运行测试容器
    docker run -d --name hermes-web-test -p 5001:5000 ${image_name}:${tag}
    
    # 等待应用启动
    sleep 5
    
    # 测试健康检查
    if curl -s http://localhost:5001/api/health | grep -q "healthy"; then
        print_info "✅ 应用健康检查通过"
    else
        print_warning "⚠️  健康检查失败，但容器仍在运行"
    fi
    
    # 显示容器日志
    print_info "容器日志:"
    docker logs hermes-web-test --tail=10
    
    # 停止测试容器
    docker stop hermes-web-test
    docker rm hermes-web-test
    
    print_info "✅ 镜像测试完成"
}

# 生成使用说明
generate_usage() {
    local image_name=$1
    
    cat << EOF

==========================================
🎉 Docker 镜像构建完成！
==========================================

📦 镜像信息:
   名称: ${image_name}
   标签: latest
   大小: $(docker images ${image_name}:latest --format "{{.Size}}")

🚀 运行命令:
   # 简单运行
   docker run -d -p 5000:5000 --name hermes-web ${image_name}:latest
   
   # 带环境变量
   docker run -d -p 5000:5000 -e PORT=5000 --name hermes-web ${image_name}:latest
   
   # 使用 Docker Compose
   docker-compose up -d

🌐 访问地址:
   本地: http://localhost:5000
   网络: http://<服务器IP>:5000

🔧 管理命令:
   # 查看日志
   docker logs -f hermes-web
   
   # 进入容器
   docker exec -it hermes-web bash
   
   # 停止容器
   docker stop hermes-web
   
   # 删除容器
   docker rm hermes-web

📊 验证运行:
   curl http://localhost:5000/api/health

==========================================
EOF
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "    Hermes Web Demo - Docker 镜像构建"
    echo "=========================================="
    echo ""
    
    # 检查 Docker
    check_docker
    
    # 获取 Docker Hub 用户名
    DOCKERHUB_USERNAME=""
    if [ $# -ge 1 ]; then
        DOCKERHUB_USERNAME=$1
    else
        # 尝试从 Docker 配置获取用户名
        if check_docker_login; then
            DOCKERHUB_USERNAME=$(docker info 2>/dev/null | grep "Username" | awk '{print $2}')
        fi
        
        if [ -z "$DOCKERHUB_USERNAME" ]; then
            read -p "请输入 Docker Hub 用户名: " DOCKERHUB_USERNAME
        fi
    fi
    
    if [ -z "$DOCKERHUB_USERNAME" ]; then
        print_error "未提供 Docker Hub 用户名"
        print_info "使用方法: $0 [DOCKERHUB_USERNAME]"
        exit 1
    fi
    
    # 镜像名称
    IMAGE_NAME="${DOCKERHUB_USERNAME}/hermes-web-demo"
    TAG="latest"
    
    print_info "Docker Hub 用户名: ${DOCKERHUB_USERNAME}"
    print_info "镜像名称: ${IMAGE_NAME}:${TAG}"
    
    # 构建镜像
    build_image ${IMAGE_NAME} ${TAG}
    
    # 测试镜像
    test_image ${IMAGE_NAME} ${TAG}
    
    # 推送镜像（可选）
    echo ""
    read -p "是否推送镜像到 Docker Hub? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        push_image ${IMAGE_NAME} ${TAG}
    else
        print_info "跳过镜像推送"
    fi
    
    # 生成使用说明
    generate_usage ${IMAGE_NAME}
    
    print_info "✅ 所有操作完成！"
}

# 执行主函数
main "$@"