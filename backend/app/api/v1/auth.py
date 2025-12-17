"""
Authentication API Endpoints

Endpoints for login, logout, and user profile
"""

from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta
import logging

from app.schemas.auth import LoginRequest, Token, User, SetupCompletionStatus
from app.services.auth.ldap_auth import LDAPAuthService
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES_REMEMBER
from app.api.dependencies.auth import get_current_user, get_optional_user
from app.services.samba.provision import SambaProvisionService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
ldap_service = LDAPAuthService()
provision_service = SambaProvisionService()


@router.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    """
    Authenticate user against Samba AD and return JWT token

    Args:
        login_request: Login credentials

    Returns:
        JWT access token

    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"Login attempt for user: {login_request.username}")

    # Authenticate via LDAP
    success, user, error = ldap_service.authenticate(
        login_request.username,
        login_request.password
    )

    if not success or user is None:
        logger.warning(f"Login failed for {login_request.username}: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error or "Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"User {user.username} authenticated successfully")

    # Create JWT token
    expires_delta = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES_REMEMBER if login_request.remember_me
        else ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token_data = {
        "sub": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "domain": user.domain,
        "groups": user.groups,
        "is_admin": user.is_admin
    }

    access_token = create_access_token(data=token_data, expires_delta=expires_delta)

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds())
    )


@router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information

    Args:
        current_user: Current user from JWT token

    Returns:
        User information
    """
    return current_user


@router.post("/auth/logout")
async def logout():
    """
    Logout user (client should discard token)

    Note: JWT tokens are stateless, so logout is handled client-side
    by discarding the token. For true server-side logout, implement
    token blacklisting.

    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}


@router.get("/auth/setup-status", response_model=SetupCompletionStatus)
async def get_setup_status(current_user: User = Depends(get_optional_user)):
    """
    Check if setup wizard is completed

    Returns:
        Setup completion status
    """
    # Check if domain is provisioned
    is_provisioned = await provision_service.is_domain_provisioned()

    # If provisioned, setup is considered complete
    # In future, could add a database flag for explicit completion tracking
    is_completed = is_provisioned

    # User can skip to dashboard if setup is complete OR if they're authenticated
    can_skip = is_completed or (current_user is not None)

    return SetupCompletionStatus(
        is_completed=is_completed,
        completed_at=None,  # TODO: Store completion timestamp in database
        can_skip_to_dashboard=can_skip
    )
