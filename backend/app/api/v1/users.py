"""User management API endpoints"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging

from app.schemas.users import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserPasswordChange,
    UserListResponse
)
from app.services.samba.users import user_service
from app.api.dependencies.auth import get_current_admin_user
from app.schemas.auth import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/users", response_model=UserListResponse)
async def list_users(current_user: User = Depends(get_current_admin_user)):
    """
    List all users

    Requires admin privileges.
    """
    try:
        users = user_service.list_users()
        return UserListResponse(
            users=users,
            total=len(users)
        )
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


@router.get("/users/{username}", response_model=UserResponse)
async def get_user(
    username: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific user's details

    Requires admin privileges.
    """
    try:
        user = user_service.get_user(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new user

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} creating user {user_data.username}")

        success = user_service.create_user(
            username=user_data.username,
            password=user_data.password,
            given_name=user_data.given_name,
            surname=user_data.surname,
            email=user_data.email,
            description=user_data.description,
            must_change_password=user_data.must_change_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        # Get the created user's details
        user = user_service.get_user(user_data.username)
        if not user:
            # User was created but we can't fetch details
            user = {
                "username": user_data.username,
                "display_name": user_data.given_name,
                "email": user_data.email,
                "description": user_data.description,
                "account_disabled": False
            }

        return user

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating user {user_data.username}: {error_msg}")

        # Parse common error messages
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {user_data.username} already exists"
            )
        elif "password" in error_msg.lower() and "complexity" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet complexity requirements"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {error_msg}"
        )


@router.put("/users/{username}", response_model=UserResponse)
async def update_user(
    username: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update user details

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} updating user {username}")

        user_service.update_user(
            username=username,
            display_name=user_data.display_name,
            email=user_data.email,
            description=user_data.description,
            admin_password=user_data.admin_password
        )

        # Get updated user details
        user = user_service.get_user(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error updating user {username}: {error_msg}")

        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {error_msg}"
        )


@router.delete("/users/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    username: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a user

    Requires admin privileges.
    """
    try:
        # Prevent self-deletion
        if username.lower() == current_user.username.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        # Prevent deletion of critical accounts
        protected_accounts = ['administrator', 'guest', 'krbtgt']
        if username.lower() in protected_accounts:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot delete protected account {username}"
            )

        logger.info(f"Admin {current_user.username} deleting user {username}")

        user_service.delete_user(username)
        return None

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting user {username}: {error_msg}")

        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {error_msg}"
        )


@router.post("/users/{username}/enable", response_model=UserResponse)
async def enable_user(
    username: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Enable a user account

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} enabling user {username}")
        user_service.enable_user(username)

        user = user_service.get_user(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling user {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable user: {str(e)}"
        )


@router.post("/users/{username}/disable", response_model=UserResponse)
async def disable_user(
    username: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Disable a user account

    Requires admin privileges.
    """
    try:
        # Prevent self-disabling
        if username.lower() == current_user.username.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot disable your own account"
            )

        logger.info(f"Admin {current_user.username} disabling user {username}")
        user_service.disable_user(username)

        user = user_service.get_user(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling user {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable user: {str(e)}"
        )


@router.post("/users/{username}/password", status_code=status.HTTP_204_NO_CONTENT)
async def set_password(
    username: str,
    password_data: UserPasswordChange,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Set a user's password

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} changing password for user {username}")

        user_service.set_password(
            username=username,
            new_password=password_data.new_password,
            must_change=password_data.must_change_at_next_login
        )

        return None

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error setting password for {username}: {error_msg}")

        if "complexity" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet complexity requirements"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set password: {error_msg}"
        )
