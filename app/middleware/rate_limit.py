import time
from typing import Dict, List, Tuple, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.
    
    This middleware limits the number of requests a client can make within a specified time window.
    It uses a sliding window algorithm to track requests.
    """
    def __init__(
        self,
        app,
        rate_limit: int = 60,  # requests per minute
        window_size: int = 60,  # window size in seconds
        block_time: int = 60,  # block time in seconds
        exclude_paths: Optional[List[str]] = None,
        exclude_methods: Optional[List[str]] = None,
        exclude_ips: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_size = window_size
        self.block_time = block_time
        self.exclude_paths = exclude_paths or ["/static", "/favicon.ico"]
        self.exclude_methods = exclude_methods or ["OPTIONS"]
        self.exclude_ips = exclude_ips or ["127.0.0.1"]
        
        # Store client request history: {client_id: [(timestamp, count), ...]}
        self.request_history: Dict[str, List[Tuple[float, int]]] = {}
        
        # Store blocked clients: {client_id: unblock_time}
        self.blocked_clients: Dict[str, float] = {}
        
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_id = self._get_client_id(request)
        
        # Skip rate limiting for excluded paths, methods, or IPs
        if self._should_exclude(request, client_id):
            return await call_next(request)
        
        # Check if client is blocked
        current_time = time.time()
        if client_id in self.blocked_clients:
            if current_time < self.blocked_clients[client_id]:
                # Client is still blocked
                return self._rate_limit_response(
                    retry_after=int(self.blocked_clients[client_id] - current_time)
                )
            else:
                # Unblock client
                del self.blocked_clients[client_id]
        
        # Check rate limit
        if self._is_rate_limited(client_id, current_time):
            # Block client
            self.blocked_clients[client_id] = current_time + self.block_time
            return self._rate_limit_response(retry_after=self.block_time)
        
        # Process the request
        return await call_next(request)
    
    def _get_client_id(self, request: Request) -> str:
        """Get a unique identifier for the client."""
        # Use X-Forwarded-For header if available (for clients behind proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP in the chain (client's IP)
            return forwarded_for.split(",")[0].strip()
        
        # Otherwise use the client's direct IP
        return request.client.host if request.client else "unknown"
    
    def _should_exclude(self, request: Request, client_id: str) -> bool:
        """Check if the request should be excluded from rate limiting."""
        # Check if path is excluded
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return True
        
        # Check if method is excluded
        if request.method in self.exclude_methods:
            return True
        
        # Check if IP is excluded
        if client_id in self.exclude_ips:
            return True
        
        return False
    
    def _is_rate_limited(self, client_id: str, current_time: float) -> bool:
        """Check if the client has exceeded the rate limit."""
        # Initialize client history if not exists
        if client_id not in self.request_history:
            self.request_history[client_id] = [(current_time, 1)]
            return False
        
        # Clean up old requests outside the window
        window_start = current_time - self.window_size
        self.request_history[client_id] = [
            (ts, count) for ts, count in self.request_history[client_id]
            if ts >= window_start
        ]
        
        # Count requests in the current window
        total_requests = sum(count for _, count in self.request_history[client_id])
        
        # Add current request
        self.request_history[client_id].append((current_time, 1))
        
        # Check if rate limit is exceeded
        return total_requests >= self.rate_limit
    
    def _rate_limit_response(self, retry_after: int) -> Response:
        """Create a rate limit exceeded response."""
        content = {
            "error": "Rate limit exceeded",
            "detail": f"Too many requests. Please try again after {retry_after} seconds."
        }
        
        response = Response(
            content=str(content),
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            media_type="application/json"
        )
        
        # Set Retry-After header
        response.headers["Retry-After"] = str(retry_after)
        
        return response
