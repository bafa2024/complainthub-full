# backend/app/middleware/security.py

import logging
import time
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from app.core.security import security_manager
import json

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Enterprise security middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            # Extract request data for security analysis
            request_data = {
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "path": request.url.path,
                "method": request.method,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params)
            }
            
            # Get request body for payload analysis
            try:
                body = await request.body()
                if body:
                    request_data["payload"] = body.decode('utf-8', errors='ignore')
            except:
                request_data["payload"] = ""
            
            # Process request through security manager
            security_result = security_manager.process_request(request_data)
            
            if not security_result["allowed"]:
                # Block request due to security threats
                response = JSONResponse(
                    status_code=403,
                    content={
                        "error": "Access denied",
                        "reason": "Security threat detected",
                        "threats": security_result["threats"]
                    }
                )
                await response(scope, receive, send)
                return
            
            # Add security headers
            async def send_with_security_headers(message):
                if message["type"] == "http.response.start":
                    # Add security headers
                    headers = message.get("headers", [])
                    headers.extend([
                        (b"X-Content-Type-Options", b"nosniff"),
                        (b"X-Frame-Options", b"DENY"),
                        (b"X-XSS-Protection", b"1; mode=block"),
                        (b"Strict-Transport-Security", b"max-age=31536000; includeSubDomains"),
                        (b"Content-Security-Policy", b"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"),
                        (b"Referrer-Policy", b"strict-origin-when-cross-origin"),
                        (b"Permissions-Policy", b"geolocation=(), microphone=(), camera=()"),
                        (b"X-Permitted-Cross-Domain-Policies", b"noneonly"),
                    ])
                    message["headers"] = headers
                
                await send(message)
            
            # Continue with the request
            await self.app(scope, receive, send_with_security_headers)
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            # Continue with request even if security check fails
            await self.app(scope, receive, send)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request, "client"):
            return request.client.host
        
        return "unknown"

class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 100):
        self.app = app
        self.requests_per_minute = requests_per_minute
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not security_manager.check_rate_limit(client_ip, self.requests_per_minute, 60):
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": "Rate limit exceeded. Please try again later."
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client"):
            return request.client.host
        
        return "unknown"

class AuditMiddleware:
    """Audit logging middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Capture request details
        request_data = {
            "method": request.method,
            "path": request.url.path,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": time.time()
        }
        
        # Get user info if authenticated
        try:
            # This would need to be implemented based on your auth system
            user_id = None  # Extract from request if available
            request_data["user_id"] = user_id
        except:
            pass
        
        # Log request
        security_manager.log_security_event("REQUEST_STARTED", request_data)
        
        # Process request
        try:
            await self.app(scope, receive, send)
            
            # Log successful response
            end_time = time.time()
            response_data = {
                **request_data,
                "duration": end_time - start_time,
                "status": "success"
            }
            security_manager.log_security_event("REQUEST_COMPLETED", response_data)
            
        except Exception as e:
            # Log error
            end_time = time.time()
            error_data = {
                **request_data,
                "duration": end_time - start_time,
                "status": "error",
                "error": str(e)
            }
            security_manager.log_security_event("REQUEST_ERROR", error_data)
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client"):
            return request.client.host
        
        return "unknown"

class CORSMiddleware:
    """CORS middleware with security considerations"""
    
    def __init__(self, app, allowed_origins: list = None):
        self.app = app
        self.allowed_origins = allowed_origins or ["http://localhost:3000"]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        origin = request.headers.get("origin")
        
        async def send_with_cors(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                
                # Add CORS headers only for allowed origins
                if origin in self.allowed_origins:
                    headers.extend([
                        (b"Access-Control-Allow-Origin", origin.encode()),
                        (b"Access-Control-Allow-Methods", b"GET, POST, PUT, DELETE, OPTIONS"),
                        (b"Access-Control-Allow-Headers", b"Content-Type, Authorization"),
                        (b"Access-Control-Allow-Credentials", b"true"),
                    ])
                
                message["headers"] = headers
            
            await send(message)
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            await response(scope, receive, send_with_cors)
            return
        
        await self.app(scope, receive, send_with_cors) 