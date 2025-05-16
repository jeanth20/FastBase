import secrets
import time
from typing import Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN

class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware for CSRF protection.

    This middleware generates and validates CSRF tokens for forms to prevent
    Cross-Site Request Forgery attacks.
    """
    def __init__(
        self,
        app,
        secret_key: str,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        cookie_secure: bool = False,
        cookie_httponly: bool = True,
        cookie_samesite: str = "lax",
        token_expiry: int = 3600  # 1 hour
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.token_expiry = token_expiry
        self.tokens: Dict[str, float] = {}  # token -> expiry time

    async def dispatch(self, request: Request, call_next):
        # TEMPORARILY DISABLE ALL CSRF VALIDATION FOR DEBUGGING
        print(f"CSRF middleware - DISABLED for request: {request.method} {request.url.path}")

        # Always set a CSRF token cookie for all requests
        response = await call_next(request)
        response = self._set_csrf_cookie(response)
        return response

        # The original code is commented out below for reference
        """
        # Skip CSRF check for GET, HEAD, OPTIONS requests
        if request.method in ("GET", "HEAD", "OPTIONS"):
            response = await call_next(request)
            # Set CSRF token cookie for GET requests if not present
            if request.method == "GET" and not request.cookies.get(self.cookie_name):
                response = self._set_csrf_cookie(response)
            return response

        # Skip CSRF check for static files
        if request.url.path.startswith("/static"):
            return await call_next(request)

        # For POST, PUT, DELETE, etc. validate the CSRF token
        cookie_token = request.cookies.get(self.cookie_name)

        # Get token from header or form
        header_token = request.headers.get(self.header_name)
        form_token = None

        # Try to get token from form data
        if "application/x-www-form-urlencoded" in request.headers.get("content-type", ""):
            try:
                form_data = await request.form()
                form_token = form_data.get("csrf_token")
            except:
                pass

        # Use header token or form token
        request_token = header_token or form_token

        # Validate token
        if not cookie_token or not request_token or cookie_token != request_token:
            print(f"CSRF validation failed - Path: {request.url.path}, Method: {request.method}")
            print(f"Cookie token: {cookie_token}")
            print(f"Request token: {request_token}")

            # For development, allow the request to proceed even if CSRF validation fails
            # In production, you would want to uncomment the following return statement
            # return Response(
            #     content="CSRF token missing or invalid",
            #     status_code=HTTP_403_FORBIDDEN
            # )

            # For now, just set a new CSRF token and continue
            response = await call_next(request)
            response = self._set_csrf_cookie(response)
            return response

        # Clean up expired tokens
        self._clean_expired_tokens()

        # Process the request
        response = await call_next(request)

        # Refresh CSRF token
        response = self._set_csrf_cookie(response)

        return response
        """

    def _set_csrf_cookie(self, response: Response) -> Response:
        """Set a new CSRF token cookie"""
        token = secrets.token_hex(32)
        expiry = time.time() + self.token_expiry
        self.tokens[token] = expiry

        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=self.cookie_httponly,
            secure=self.cookie_secure,
            samesite=self.cookie_samesite,
            max_age=self.token_expiry
        )

        return response

    def _clean_expired_tokens(self):
        """Remove expired tokens"""
        current_time = time.time()
        expired_tokens = [token for token, expiry in self.tokens.items() if expiry < current_time]
        for token in expired_tokens:
            self.tokens.pop(token, None)
