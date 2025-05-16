from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_from_cookie
from app.models.user import User
from app.services.auth import verify_password, get_password_hash
from app.services.user_activity import get_user_activities
from app.services.notification_service import get_unread_notification_count

router = APIRouter(tags=["pages"])

@router.get("/")
async def home(request: Request):
    """
    Render the home page
    """
    return request.app.state.templates.TemplateResponse(
        "pages/home.html",
        {"request": request}
    )

@router.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Render the dashboard page
    """
    print("Dashboard route - Starting dashboard route handler")

    # Check if the user is logged in by looking for the access_token cookie
    token = request.cookies.get("access_token")
    if not token:
        print("Dashboard route - No access_token cookie found")
        return RedirectResponse(url="/auth/login", status_code=303)

    print(f"Dashboard route - Found access_token cookie: {token[:10]}...")

    try:
        # Get the user from the token
        from app.services.auth import get_user_by_username
        from jose import jwt
        from app.config import settings

        # Process the token
        if token.startswith("Bearer "):
            token = token[7:]

        # Decode the token
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            username = payload.get("sub")
            if not username:
                print("Dashboard route - No username in token")
                return RedirectResponse(url="/auth/login", status_code=303)

            print(f"Dashboard route - Username from token: {username}")

            # Get the user directly from the database
            user = get_user_by_username(db, username)
            if not user:
                print(f"Dashboard route - User not found: {username}")
                return RedirectResponse(url="/auth/login", status_code=303)

            print(f"Dashboard route - User found: {user.username}")

            # Set user ID in request state for activity logging
            request.state.user_id = user.id

            # Get user activities
            try:
                activities = get_user_activities(db, user.id, limit=10)
            except Exception as e:
                print(f"Dashboard route - Error getting activities: {str(e)}")
                activities = []

            # Get unread notification count
            try:
                unread_notification_count = get_unread_notification_count(db, user.id)
            except Exception as e:
                print(f"Dashboard route - Error getting notification count: {str(e)}")
                unread_notification_count = 0

            # Render the dashboard template
            print("Dashboard route - Rendering dashboard template")
            return request.app.state.templates.TemplateResponse(
                "pages/dashboard.html",
                {
                    "request": request,
                    "user": user,
                    "activities": activities,
                    "unread_notification_count": unread_notification_count
                }
            )

        except Exception as jwt_error:
            print(f"Dashboard route - JWT decode error: {str(jwt_error)}")
            return RedirectResponse(url="/auth/login", status_code=303)

    except Exception as e:
        # Log the error and redirect to login page
        print(f"Dashboard route - Unexpected error: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=303)

@router.get("/profile")
async def profile_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Render the profile page
    """
    # Get the current user from the cookie
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Set user ID in request state for activity logging
        request.state.user_id = current_user.id

        # Get unread notification count
        try:
            unread_notification_count = get_unread_notification_count(db, current_user.id)
        except Exception as e:
            print(f"Error getting notification count: {str(e)}")
            unread_notification_count = 0

        return request.app.state.templates.TemplateResponse(
            "pages/profile.html",
            {
                "request": request,
                "user": current_user,
                "unread_notification_count": unread_notification_count
            }
        )
    except:
        # Redirect to login page if not authenticated
        return RedirectResponse(url="/auth/login", status_code=303)

@router.post("/profile")
async def update_profile(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    """
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Set user ID in request state for activity logging
        request.state.user_id = current_user.id

        # Update user email
        current_user.email = email
        db.commit()

        return request.app.state.templates.TemplateResponse(
            "pages/profile.html",
            {
                "request": request,
                "user": current_user,
                "success": "Profile updated successfully"
            }
        )
    except HTTPException as e:
        return request.app.state.templates.TemplateResponse(
            "pages/profile.html",
            {
                "request": request,
                "user": current_user,
                "error": e.detail
            }
        )
    except:
        # Redirect to login page if not authenticated
        return RedirectResponse(url="/auth/login", status_code=303)

@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Set user ID in request state for activity logging
        request.state.user_id = current_user.id

        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            return request.app.state.templates.TemplateResponse(
                "pages/profile.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": "Current password is incorrect"
                }
            )

        # Verify new password matches confirmation
        if new_password != confirm_password:
            return request.app.state.templates.TemplateResponse(
                "pages/profile.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": "New passwords do not match"
                }
            )

        # Update password
        current_user.hashed_password = get_password_hash(new_password)
        db.commit()

        return request.app.state.templates.TemplateResponse(
            "pages/profile.html",
            {
                "request": request,
                "user": current_user,
                "success": "Password changed successfully"
            }
        )
    except HTTPException as e:
        return request.app.state.templates.TemplateResponse(
            "pages/profile.html",
            {
                "request": request,
                "user": current_user,
                "error": e.detail
            }
        )
    except:
        # Redirect to login page if not authenticated
        return RedirectResponse(url="/auth/login", status_code=303)

@router.get("/activity")
async def activity_log(
    request: Request,
    activity_type: Optional[str] = None,
    page: int = 1,
    db: Session = Depends(get_db)
):
    """
    Render the activity log page
    """
    # Get the current user from the cookie
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Set user ID in request state for activity logging
        request.state.user_id = current_user.id

        # Pagination settings
        page_size = 20
        skip = (page - 1) * page_size

        # Get user activities with filtering and pagination
        query = db.query(User.activities).filter(User.id == current_user.id)

        if activity_type:
            query = query.filter(User.activities.activity_type == activity_type)

        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size

        activities = get_user_activities(
            db,
            current_user.id,
            skip=skip,
            limit=page_size,
            activity_type=activity_type
        )

        # Get unread notification count
        try:
            unread_notification_count = get_unread_notification_count(db, current_user.id)
        except Exception as e:
            print(f"Error getting notification count: {str(e)}")
            unread_notification_count = 0

        return request.app.state.templates.TemplateResponse(
            "pages/activity.html",
            {
                "request": request,
                "user": current_user,
                "activities": activities,
                "activity_type": activity_type,
                "page": page,
                "total_pages": total_pages,
                "unread_notification_count": unread_notification_count
            }
        )
    except:
        # Redirect to login page if not authenticated
        return RedirectResponse(url="/auth/login", status_code=303)

@router.get("/components")
async def components(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Render the components showcase page
    """
    # Get the current user from the cookie
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Set user ID in request state for activity logging
        request.state.user_id = current_user.id

        # Get unread notification count
        try:
            unread_notification_count = get_unread_notification_count(db, current_user.id)
        except Exception as e:
            print(f"Error getting notification count: {str(e)}")
            unread_notification_count = 0

        return request.app.state.templates.TemplateResponse(
            "pages/components.html",
            {
                "request": request,
                "user": current_user,
                "unread_notification_count": unread_notification_count
            }
        )
    except:
        # Redirect to login page if not authenticated
        return RedirectResponse(url="/auth/login", status_code=303)