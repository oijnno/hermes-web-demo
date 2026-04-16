"""
中间件配置
"""

import time
from fastapi import Request
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging import setup_logging

logger = setup_logging()

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"请求开始: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"请求完成: {request.method} {request.url.path} "
                f"状态码: {response.status_code} "
                f"耗时: {process_time:.3f}s"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"请求错误: {request.method} {request.url.path} "
                f"错误: {str(e)} "
                f"耗时: {process_time:.3f}s"
            )
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

def setup_middleware(app):
    """设置所有中间件"""
    
    # GZip 压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 安全头
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 日志
    app.add_middleware(LoggingMiddleware)