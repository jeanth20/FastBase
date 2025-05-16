from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_from_cookie
from app.models.user import User
from app.models.notification import Notification
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
async def notifications_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Notifications page
    """
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Get user notifications
        try:
            notifications = notification_service.get_user_notifications(db, current_user.id)
        except Exception as e:
            print(f"Error getting notifications: {str(e)}")
            notifications = []

        return request.app.state.templates.TemplateResponse(
            "pages/notifications.html",
            {
                "request": request,
                "user": current_user,
                "notifications": notifications
            }
        )
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/auth/login", status_code=303)
        raise e


@router.get("/api/list")
async def get_notifications(
    request: Request,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    API endpoint to get notifications
    """
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Get user notifications
        try:
            notifications = notification_service.get_user_notifications(
                db,
                current_user.id,
                unread_only=unread_only
            )
        except Exception as e:
            print(f"Error getting notifications for API: {str(e)}")
            notifications = []

        # Format notifications for API response
        result = []
        for notification in notifications:
            result.append({
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
                "link": notification.link
            })

        return {"notifications": result}
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return {"error": "Not authenticated"}
        raise e


@router.post("/api/{notification_id}/read")
async def mark_as_read(
    request: Request,
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    API endpoint to mark a notification as read
    """
    try:
        current_user = await get_current_user_from_cookie(request, db)

        notification = notification_service.mark_notification_as_read(
            db, notification_id, current_user.id
        )

        if not notification:
            return {"success": False, "error": "Notification not found"}

        return {"success": True}
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return {"error": "Not authenticated"}
        raise e


@router.post("/api/read-all")
async def mark_all_as_read(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    API endpoint to mark all notifications as read
    """
    try:
        current_user = await get_current_user_from_cookie(request, db)

        count = notification_service.mark_all_notifications_as_read(db, current_user.id)

        return {"success": True, "count": count}
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return {"error": "Not authenticated"}
        raise e


@router.delete("/api/{notification_id}")
async def delete_notification(
    request: Request,
    notification_id: int,
    db: Session = Depends(get_db)
):
    """
    API endpoint to delete a notification
    """
    try:
        current_user = await get_current_user_from_cookie(request, db)

        success = notification_service.delete_notification(
            db, notification_id, current_user.id
        )

        if not success:
            return {"success": False, "error": "Notification not found"}

        return {"success": True}
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return {"error": "Not authenticated"}
        raise e
