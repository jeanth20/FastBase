from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.auth import get_user_by_username

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the current user from the JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get the user from the database
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception

    return user

async def get_current_user_from_cookie(request, db: Session):
    """
    Get the current user from the cookie
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    # Get token from cookie with detailed logging
    token = request.cookies.get("access_token")
    print(f"get_current_user_from_cookie - Cookie token: {token}")

    if not token:
        print("get_current_user_from_cookie - No access_token cookie found")
        raise credentials_exception

    # Remove Bearer prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
        print("get_current_user_from_cookie - Bearer prefix removed")
    else:
        print("get_current_user_from_cookie - No Bearer prefix found")
        # Add Bearer prefix if it's missing - this is a workaround for testing
        # In production, you would want to ensure consistent token format
        token = f"Bearer {token}"
        print("get_current_user_from_cookie - Added Bearer prefix for testing")
        token = token[7:]  # Remove it again for processing

    try:
        # Decode the JWT token
        print(f"get_current_user_from_cookie - Attempting to decode token: {token[:10]}...")
        print(f"get_current_user_from_cookie - Using secret key: {settings.SECRET_KEY[:5]}...")
        print(f"get_current_user_from_cookie - Using algorithm: {settings.ALGORITHM}")

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        print(f"get_current_user_from_cookie - Token decoded successfully: {payload}")

        username: str = payload.get("sub")
        if username is None:
            print("get_current_user_from_cookie - No 'sub' claim in token")
            raise credentials_exception

        print(f"get_current_user_from_cookie - Username from token: {username}")
    except JWTError as e:
        # Log the error for debugging
        print(f"get_current_user_from_cookie - JWT Error: {str(e)}")
        raise credentials_exception

    # Get the user from the database
    print(f"get_current_user_from_cookie - Looking up user: {username}")
    user = get_user_by_username(db, username)
    if user is None:
        print(f"get_current_user_from_cookie - User not found: {username}")
        raise credentials_exception

    print(f"get_current_user_from_cookie - User found: {user.username}")

    # Check if user is active
    if not user.is_active:
        print(f"get_current_user_from_cookie - User is inactive: {username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    print(f"get_current_user_from_cookie - Authentication successful for: {username}")
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    Check if the current user is an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return current_user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Check if the current user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
