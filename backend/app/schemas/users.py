"""User management schemas"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=1, max_length=64)
    display_name: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class UserCreate(BaseModel):
    """Schema for creating a user"""
    username: str = Field(..., min_length=1, max_length=64, pattern=r'^[a-zA-Z0-9._-]+$')
    password: str = Field(..., min_length=8)
    given_name: Optional[str] = Field(None, max_length=64)
    surname: Optional[str] = Field(None, max_length=64)
    email: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    must_change_password: bool = True

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username doesn't contain invalid characters"""
        if not v:
            raise ValueError('Username cannot be empty')
        # Check for reserved names
        reserved = ['administrator', 'guest', 'krbtgt']
        if v.lower() in reserved:
            raise ValueError(f'Username {v} is reserved')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    display_name: Optional[str] = Field(None, max_length=64)
    email: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    admin_password: str = Field(..., min_length=1)


class UserPasswordChange(BaseModel):
    """Schema for changing user password"""
    new_password: str = Field(..., min_length=8)
    must_change_at_next_login: bool = False


class UserResponse(UserBase):
    """User response schema"""
    account_disabled: bool = False


class UserListResponse(BaseModel):
    """Response for user list"""
    users: list[UserResponse]
    total: int
