from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_from_cookie
from app.models.user import User
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_user
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login_page(request: Request):
    """
    Render the login page
    """
    return request.app.state.templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handle login form submission
    """
    print(f"Login POST route - Processing login for username: {username}")

    user = authenticate_user(db, username, password)
    if not user:
        print(f"Login POST route - Authentication failed for username: {username}")
        return request.app.state.templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Invalid username or password"
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    print(f"Login POST route - Authentication successful for user: {user.username}")

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    print(f"Login POST route - Access token created")

    # Use a two-step approach to ensure the cookie is set before redirection
    print(f"Login POST route - Using two-step approach with cookie setting")

    # First, create a simple HTML response with JavaScript redirection
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login Successful</title>
        <script>
            // Log that we're about to redirect
            console.log('Login successful, redirecting to dashboard...');

            // Check if the cookie is set
            console.log('Cookies:', document.cookie);

            // Redirect after a short delay to ensure the cookie is set
            setTimeout(function() {{
                window.location.href = '/dashboard';
            }}, 500);
        </script>
    </head>
    <body>
        <h1>Login Successful!</h1>
        <p>Redirecting to dashboard...</p>
    </body>
    </html>
    """

    # Create a response with the HTML content
    response = Response(content=html_content, media_type="text/html")

    # Set the cookie on the response
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    print(f"Login POST route - Cookie set, using HTML with JavaScript redirect to dashboard")

    # Set user ID in request state for activity logging
    request.state.user_id = user.id

    return response

@router.get("/register")
async def register_page(request: Request):
    """
    Render the registration page
    """
    return request.app.state.templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handle registration form submission
    """
    # Validate password confirmation
    if password != confirm_password:
        return request.app.state.templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Passwords do not match",
                "username": username,
                "email": email
            }
        )

    try:
        # Create new user
        user = create_user(db, username, email, password)

        # Redirect to login page using direct redirection
        print("Register route - Registration successful, redirecting to login")
        return RedirectResponse(
            url="/auth/login?registered=true",
            status_code=303
        )
    except HTTPException as e:
        return request.app.state.templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": e.detail,
                "username": username,
                "email": email
            }
        )

@router.get("/logout")
async def logout(request: Request):
    """
    Handle logout
    """
    # Set user ID in request state for activity logging
    current_user: Optional[User] = None
    try:
        current_user = await get_current_user_from_cookie(request, next(get_db()))
        request.state.user_id = current_user.id
    except:
        pass

    # Clear the token cookie
    print("Logout route - Clearing token cookie")
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    print("Logout route - Cookie cleared, using direct redirect to home")

    return response

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login endpoint
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
