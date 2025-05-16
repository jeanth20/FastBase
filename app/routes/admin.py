from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_from_cookie
from app.models.user import User
from app.models.user_activity import UserActivity
from app.services.auth import create_user, get_password_hash


router = APIRouter(prefix="/admin", tags=["admin"])

async def get_admin_user(request: Request, db: Session = Depends(get_db)):
    """
    Get the current admin user from the token in cookies
    """
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Check if user is admin
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource"
            )

        # Set user ID in request state for activity logging
        request.state.user_id = current_user.id

        return current_user
    except:
        # Redirect to login page if not authenticated or not admin
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

@router.get("/dashboard")
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Admin dashboard page
    """
    try:
        current_user = await get_admin_user(request, db)

        # Get user count
        user_count = db.query(User).count()

        # Get recent users
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()

        # Get recent activities
        recent_activities = db.query(UserActivity).order_by(
            UserActivity.timestamp.desc()
        ).limit(10).all()

        return request.app.state.templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "user": current_user,
                "user_count": user_count,
                "recent_users": recent_users,
                "recent_activities": recent_activities
            }
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/auth/login", status_code=303)
        raise e

@router.get("/users")
async def admin_users(
    request: Request,
    page: int = 1,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Admin users management page
    """
    try:
        current_user = await get_admin_user(request, db)

        # Pagination settings
        page_size = 20
        skip = (page - 1) * page_size

        # Base query
        query = db.query(User)

        # Apply search filter if provided
        if search:
            query = query.filter(
                (User.username.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%"))
            )

        # Get total count for pagination
        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size

        # Get users with pagination
        users = query.order_by(User.created_at.desc()).offset(skip).limit(page_size).all()

        return request.app.state.templates.TemplateResponse(
            "admin/users.html",
            {
                "request": request,
                "user": current_user,
                "users": users,
                "page": page,
                "total_pages": total_pages,
                "search": search
            }
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/auth/login", status_code=303)
        raise e

@router.get("/users/{user_id}")
async def admin_user_detail(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Admin user detail page
    """
    try:
        current_user = await get_admin_user(request, db)

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get user activities
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(UserActivity.timestamp.desc()).limit(20).all()

        return request.app.state.templates.TemplateResponse(
            "admin/user_detail.html",
            {
                "request": request,
                "user": current_user,
                "target_user": user,
                "activities": activities
            }
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/auth/login", status_code=303)
        raise e

@router.post("/users/{user_id}/toggle-admin")
async def toggle_admin_status(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Toggle admin status for a user
    """
    try:
        current_user = await get_admin_user(request, db)

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent self-demotion
        if user.id == current_user.id:
            return request.app.state.templates.TemplateResponse(
                "admin/user_detail.html",
                {
                    "request": request,
                    "user": current_user,
                    "target_user": user,
                    "error": "You cannot change your own admin status"
                }
            )

        # Toggle admin status
        user.is_admin = not user.is_admin
        db.commit()

        return RedirectResponse(
            url=f"/admin/users/{user_id}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/auth/login", status_code=303)
        raise e

@router.post("/users/{user_id}/toggle-active")
async def toggle_active_status(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Toggle active status for a user
    """
    try:
        current_user = await get_admin_user(request, db)

        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent self-deactivation
        if user.id == current_user.id:
            return request.app.state.templates.TemplateResponse(
                "admin/user_detail.html",
                {
                    "request": request,
                    "user": current_user,
                    "target_user": user,
                    "error": "You cannot change your own active status"
                }
            )

        # Toggle active status
        user.is_active = not user.is_active
        db.commit()

        return RedirectResponse(
            url=f"/admin/users/{user_id}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/auth/login", status_code=303)
        raise e

@router.get("/create-admin")
async def create_admin_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Page to create a new admin user
    """
    try:
        current_user = await get_admin_user(request, db)

        return request.app.state.templates.TemplateResponse(
            "admin/create_admin.html",
            {"request": request, "user": current_user}
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/auth/login", status_code=303)
        raise e

@router.post("/create-admin")
async def create_admin_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create a new admin user
    """
    try:
        current_user = await get_admin_user(request, db)

        # Validate password confirmation
        if password != confirm_password:
            return request.app.state.templates.TemplateResponse(
                "admin/create_admin.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": "Passwords do not match",
                    "username": username,
                    "email": email
                }
            )

        try:
            # Create new user with admin privileges
            new_user = create_user(db, username, email, password)

            # Set admin flag
            new_user.is_admin = True
            db.commit()

            return RedirectResponse(
                url="/admin/users",
                status_code=status.HTTP_303_SEE_OTHER
            )
        except HTTPException as e:
            return request.app.state.templates.TemplateResponse(
                "admin/create_admin.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": e.detail,
                    "username": username,
                    "email": email
                }
            )
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/auth/login", status_code=303)
        raise e
