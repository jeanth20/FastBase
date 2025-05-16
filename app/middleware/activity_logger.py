from fastapi import Request
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import SessionLocal
from app.services.user_activity import log_user_activity

class ActivityLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)
        
        # Skip logging for static files
        if request.url.path.startswith("/static"):
            return response
        
        # Get user ID from request state if user is authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            # Get client information
            ip_address = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            # Determine activity type based on the endpoint
            activity_type = "page_view"
            if request.url.path.endswith("/login"):
                activity_type = "login"
            elif request.url.path.endswith("/logout"):
                activity_type = "logout"
            
            # Log the activity
            db = SessionLocal()
            try:
                log_user_activity(
                    db=db,
                    user_id=user_id,
                    activity_type=activity_type,
                    endpoint=request.url.path,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            finally:
                db.close()
        
        return response
