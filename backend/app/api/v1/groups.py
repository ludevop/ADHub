"""Group management API endpoints"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging

from app.schemas.groups import (
    GroupResponse,
    GroupCreate,
    GroupUpdate,
    GroupMemberOperation,
    GroupListResponse
)
from app.services.samba.groups import group_service
from app.api.dependencies.auth import get_current_admin_user
from app.schemas.auth import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/groups", response_model=GroupListResponse)
async def list_groups(current_user: User = Depends(get_current_admin_user)):
    """
    List all groups

    Requires admin privileges.
    """
    try:
        groups = group_service.list_groups()
        return GroupListResponse(
            groups=groups,
            total=len(groups)
        )
    except Exception as e:
        logger.error(f"Error listing groups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list groups: {str(e)}"
        )


@router.get("/groups/{groupname}", response_model=GroupResponse)
async def get_group(
    groupname: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific group's details

    Requires admin privileges.
    """
    try:
        group = group_service.get_group(groupname)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {groupname} not found"
            )
        return group
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group {groupname}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group: {str(e)}"
        )


@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new group

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} creating group {group_data.name}")

        success = group_service.create_group(
            groupname=group_data.name,
            description=group_data.description
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create group"
            )

        # Get the created group's details
        group = group_service.get_group(group_data.name)
        if not group:
            # Group was created but we can't fetch details
            group = {
                "name": group_data.name,
                "description": group_data.description,
                "members": []
            }

        return group

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating group {group_data.name}: {error_msg}")

        # Parse common error messages
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Group {group_data.name} already exists"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create group: {error_msg}"
        )


@router.put("/groups/{groupname}", response_model=GroupResponse)
async def update_group(
    groupname: str,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update group details

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} updating group {groupname}")

        group_service.update_group(
            groupname=groupname,
            description=group_data.description,
            admin_password=group_data.admin_password
        )

        # Get updated group details
        group = group_service.get_group(groupname)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {groupname} not found"
            )

        return group

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error updating group {groupname}: {error_msg}")

        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {groupname} not found"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update group: {error_msg}"
        )


@router.delete("/groups/{groupname}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    groupname: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a group

    Requires admin privileges.
    """
    try:
        # Prevent deletion of critical groups
        protected_groups = [
            'administrators', 'users', 'guests',
            'domain admins', 'domain users', 'domain guests',
            'enterprise admins', 'schema admins', 'dns admins'
        ]
        if groupname.lower() in protected_groups:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot delete protected group {groupname}"
            )

        logger.info(f"Admin {current_user.username} deleting group {groupname}")

        group_service.delete_group(groupname)
        return None

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting group {groupname}: {error_msg}")

        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {groupname} not found"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete group: {error_msg}"
        )


@router.post("/groups/{groupname}/members", response_model=GroupResponse)
async def add_member(
    groupname: str,
    member_data: GroupMemberOperation,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Add a user to a group

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} adding {member_data.username} to group {groupname}")

        group_service.add_member(groupname, member_data.username)

        group = group_service.get_group(groupname)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {groupname} not found"
            )

        return group

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error adding member to group {groupname}: {error_msg}")

        if "already a member" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {member_data.username} is already a member of {groupname}"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add member: {error_msg}"
        )


@router.delete("/groups/{groupname}/members/{username}", response_model=GroupResponse)
async def remove_member(
    groupname: str,
    username: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Remove a user from a group

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} removing {username} from group {groupname}")

        group_service.remove_member(groupname, username)

        group = group_service.get_group(groupname)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {groupname} not found"
            )

        return group

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error removing member from group {groupname}: {error_msg}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove member: {error_msg}"
        )
