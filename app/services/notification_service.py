from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.notification import Notification
from app.models.user import User


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info",
    link: Optional[str] = None
) -> Notification:
    """
    Create a new notification for a user
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        link=link
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_user_notifications(
    db: Session,
    user_id: int,
    limit: int = 10,
    skip: int = 0,
    unread_only: bool = False
) -> List[Notification]:
    """
    Get notifications for a user
    """
    try:
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    except Exception as e:
        # Handle the case where the notifications table doesn't exist yet
        print(f"Error getting user notifications: {str(e)}")
        return []


def get_unread_notification_count(db: Session, user_id: int) -> int:
    """
    Get the count of unread notifications for a user
    """
    try:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    except Exception as e:
        # Handle the case where the notifications table doesn't exist yet
        print(f"Error getting unread notification count: {str(e)}")
        return 0


def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """
    Mark a notification as read
    """
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)

        return notification
    except Exception as e:
        # Handle the case where the notifications table doesn't exist yet
        print(f"Error marking notification as read: {str(e)}")
        return None


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    """
    Mark all notifications as read for a user
    Returns the number of notifications marked as read
    """
    try:
        result = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})

        db.commit()
        return result
    except Exception as e:
        # Handle the case where the notifications table doesn't exist yet
        print(f"Error marking all notifications as read: {str(e)}")
        return 0


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    """
    Delete a notification
    Returns True if the notification was deleted, False otherwise
    """
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if notification:
            db.delete(notification)
            db.commit()
            return True

        return False
    except Exception as e:
        # Handle the case where the notifications table doesn't exist yet
        print(f"Error deleting notification: {str(e)}")
        return False
