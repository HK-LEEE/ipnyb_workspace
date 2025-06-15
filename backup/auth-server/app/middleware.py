"""
Middleware for rate limiting and security
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using in-memory storage"""
    
    def __init__(self, app, requests_per_minute: int = None, block_duration_minutes: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.rate_limit_requests_per_minute
        self.block_duration_minutes = block_duration_minutes or settings.rate_limit_block_duration_minutes
        
        # In-memory storage for rate limiting
        self.request_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.blocked_ips: Dict[str, datetime] = {}
        self.failed_attempts: Dict[str, int] = defaultdict(int)
        
        # Clean up old entries periodically
        self.last_cleanup = datetime.utcnow()
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def is_blocked(self, client_ip: str) -> bool:
        """Check if IP is currently blocked"""
        if client_ip in self.blocked_ips:
            block_time = self.blocked_ips[client_ip]
            if datetime.utcnow() - block_time < timedelta(minutes=self.block_duration_minutes):
                return True
            else:
                # Block expired, remove it
                del self.blocked_ips[client_ip]
                if client_ip in self.failed_attempts:
                    del self.failed_attempts[client_ip]
        return False
    
    def should_rate_limit(self, request: Request) -> bool:
        """Check if request should be rate limited"""
        # Only apply rate limiting to authentication endpoints
        auth_paths = ["/auth/login", "/auth/refresh", "/auth/logout"]
        return any(request.url.path.startswith(path) for path in auth_paths)
    
    def record_request(self, client_ip: str):
        """Record a request from client IP"""
        current_minute = int(datetime.utcnow().timestamp() // 60)
        self.request_counts[client_ip][current_minute] += 1
    
    def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP has exceeded rate limit"""
        current_minute = int(datetime.utcnow().timestamp() // 60)
        
        # Count requests in the last minute
        total_requests = 0
        for minute in range(current_minute - 1, current_minute + 1):
            total_requests += self.request_counts[client_ip][minute]
        
        return total_requests > self.requests_per_minute
    
    def record_failed_login(self, client_ip: str):
        """Record a failed login attempt"""
        self.failed_attempts[client_ip] += 1
        
        # Block IP after too many failed attempts
        if self.failed_attempts[client_ip] >= self.requests_per_minute:
            self.blocked_ips[client_ip] = datetime.utcnow()
            logger.warning(f"IP {client_ip} blocked due to excessive failed login attempts")
    
    def record_successful_login(self, client_ip: str):
        """Record a successful login (reset failed attempts)"""
        if client_ip in self.failed_attempts:
            del self.failed_attempts[client_ip]
        if client_ip in self.blocked_ips:
            del self.blocked_ips[client_ip]
    
    def cleanup_old_entries(self):
        """Clean up old rate limiting entries"""
        current_time = datetime.utcnow()
        
        # Only cleanup every 5 minutes
        if current_time - self.last_cleanup < timedelta(minutes=5):
            return
        
        current_minute = int(current_time.timestamp() // 60)
        
        # Remove old request counts (older than 2 minutes)
        for client_ip in list(self.request_counts.keys()):
            for minute in list(self.request_counts[client_ip].keys()):
                if current_minute - minute > 2:
                    del self.request_counts[client_ip][minute]
            
            # Remove empty client entries
            if not self.request_counts[client_ip]:
                del self.request_counts[client_ip]
        
        self.last_cleanup = current_time
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting"""
        client_ip = self.get_client_ip(request)
        
        # Clean up old entries periodically
        self.cleanup_old_entries()
        
        # Check if IP is blocked
        if self.is_blocked(client_ip):
            logger.warning(f"Blocked request from {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "IP address is temporarily blocked due to excessive failed attempts",
                    "error_code": "IP_BLOCKED"
                }
            )
        
        # Apply rate limiting only to auth endpoints
        if self.should_rate_limit(request):
            # Record this request
            self.record_request(client_ip)
            
            # Check rate limit
            if self.is_rate_limited(client_ip):
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please try again later.",
                        "error_code": "RATE_LIMIT_EXCEEDED"
                    }
                )
        
        # Process the request
        response = await call_next(request)
        
        # Record failed login attempts for further blocking
        if (request.url.path == "/auth/login" and 
            response.status_code in [401, 403]):
            self.record_failed_login(client_ip)
        elif (request.url.path == "/auth/login" and 
              response.status_code == 200):
            self.record_successful_login(client_ip)
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response 