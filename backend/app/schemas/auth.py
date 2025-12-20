"""
Authentication schemas for login, tokens, and user data
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request with username and password"""
    username: str = Field(..., description="Username (can be sAMAccountName or UPN)")
    password: str = Field(..., description="User password", min_length=1)
    remember_me: bool = Field(default=False, description="Remember login for extended session")


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Data stored in JWT token"""
    username: str
    domain: Optional[str] = None
    groups: List[str] = []
    encrypted_password: Optional[str] = None  # Encrypted user password for AD operations
    exp: Optional[datetime] = None


class User(BaseModel):
    """User information from AD"""
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    domain: str
    groups: List[str] = []
    is_admin: bool = False
    password: Optional[str] = None  # Decrypted password for AD operations


class SetupCompletionStatus(BaseModel):
    """Setup wizard completion status"""
    is_completed: bool
    completed_at: Optional[datetime] = None
    can_skip_to_dashboard: bool
