from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime

from app.config import settings
from app.middleware import ActivityLoggerMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware, CSRFMiddleware

def create_app():
    """
    Create and configure the FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Add middleware
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CSRFMiddleware, secret_key=settings.SECRET_KEY)
    app.add_middleware(RateLimitMiddleware,
                      rate_limit=60,  # 60 requests per minute
                      window_size=60,  # 1 minute window
                      block_time=300)  # 5 minute block time
    app.add_middleware(ActivityLoggerMiddleware)

    # Create and configure Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    templates.env.globals.update(now=datetime.now)

    # Import routers here to avoid circular imports
    from app.routes.auth import router as auth_router
    from app.routes.pages import router as pages_router
    from app.routes.admin import router as admin_router
    from app.routes.notifications import router as notifications_router

    # Include routers
    app.include_router(auth_router)
    app.include_router(pages_router)
    app.include_router(admin_router)
    app.include_router(notifications_router)

    # Make templates available to routes
    app.state.templates = templates

    return app

# Create app instance
app = create_app()
