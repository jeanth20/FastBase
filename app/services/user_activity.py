from sqlalchemy.orm import Session

from app.models.user_activity import UserActivity

def log_user_activity(
    db: Session,
    user_id: int,
    activity_type: str,
    endpoint: str,
    ip_address: str,
    user_agent: str
) -> UserActivity:
    """
    Log user activity
    """
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        endpoint=endpoint,
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity

def get_user_activities(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    activity_type: str = None
):
    """
    Get user activities with optional filtering by activity type
    """
    try:
        query = db.query(UserActivity).filter(UserActivity.user_id == user_id)

        if activity_type:
            query = query.filter(UserActivity.activity_type == activity_type)

        return query.order_by(
            UserActivity.timestamp.desc()
        ).offset(skip).limit(limit).all()
    except Exception as e:
        # Handle the case where the user_activities table doesn't exist yet
        print(f"Error getting user activities: {str(e)}")
        return []
