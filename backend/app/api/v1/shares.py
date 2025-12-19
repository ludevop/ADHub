"""Share management API endpoints"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging

from app.schemas.shares import (
    ShareResponse,
    ShareCreate,
    ShareUpdate,
    ShareListResponse
)
from app.services.samba.shares import share_service
from app.api.dependencies.auth import get_current_admin_user
from app.schemas.auth import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/shares", response_model=ShareListResponse)
async def list_shares(current_user: User = Depends(get_current_admin_user)):
    """
    List all shares

    Requires admin privileges.
    """
    try:
        shares = share_service.list_shares()
        return ShareListResponse(
            shares=shares,
            total=len(shares)
        )
    except Exception as e:
        logger.error(f"Error listing shares: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list shares: {str(e)}"
        )


@router.get("/shares/{sharename}", response_model=ShareResponse)
async def get_share(
    sharename: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific share's details

    Requires admin privileges.
    """
    try:
        share = share_service.get_share(sharename)
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Share {sharename} not found"
            )
        return share
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting share {sharename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get share: {str(e)}"
        )


@router.post("/shares", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def create_share(
    share_data: ShareCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new share

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} creating share {share_data.name}")

        success = share_service.create_share(
            sharename=share_data.name,
            path=share_data.path,
            comment=share_data.comment,
            read_only=share_data.read_only,
            guest_ok=share_data.guest_ok,
            browseable=share_data.browseable
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create share"
            )

        # Get the created share's details
        share = share_service.get_share(share_data.name)
        if not share:
            # Share was created but we can't fetch details
            share = {
                "name": share_data.name,
                "path": share_data.path,
                "comment": share_data.comment,
                "read_only": share_data.read_only,
                "guest_ok": share_data.guest_ok,
                "browseable": share_data.browseable
            }

        return share

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating share {share_data.name}: {error_msg}")

        # Parse common error messages
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Share {share_data.name} already exists"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create share: {error_msg}"
        )


@router.put("/shares/{sharename}", response_model=ShareResponse)
async def update_share(
    sharename: str,
    share_data: ShareUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update share details

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} updating share {sharename}")

        share_service.update_share(
            sharename=sharename,
            path=share_data.path,
            comment=share_data.comment,
            read_only=share_data.read_only,
            guest_ok=share_data.guest_ok,
            browseable=share_data.browseable
        )

        # Get updated share details
        share = share_service.get_share(sharename)
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Share {sharename} not found"
            )

        return share

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error updating share {sharename}: {error_msg}")

        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Share {sharename} not found"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update share: {error_msg}"
        )


@router.delete("/shares/{sharename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_share(
    sharename: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a share

    Requires admin privileges.
    """
    try:
        # Prevent deletion of critical shares
        protected_shares = ['homes', 'netlogon', 'sysvol']
        if sharename.lower() in protected_shares:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot delete protected share {sharename}"
            )

        logger.info(f"Admin {current_user.username} deleting share {sharename}")

        share_service.delete_share(sharename)
        return None

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting share {sharename}: {error_msg}")

        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Share {sharename} not found"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete share: {error_msg}"
        )
