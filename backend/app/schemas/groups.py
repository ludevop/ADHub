"""Group management schemas"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class GroupBase(BaseModel):
    """Base group schema"""
    name: str = Field(..., min_length=1, max_length=64)
    description: Optional[str] = None
    members: List[str] = []


class GroupCreate(BaseModel):
    """Schema for creating a group"""
    name: str = Field(..., min_length=1, max_length=64, pattern=r'^[a-zA-Z0-9._-]+$')
    description: Optional[str] = Field(None, max_length=255)

    @field_validator('name')
    @classmethod
    def validate_groupname(cls, v):
        """Validate group name doesn't contain invalid characters"""
        if not v:
            raise ValueError('Group name cannot be empty')
        # Check for reserved names
        reserved = ['administrators', 'users', 'guests', 'domain admins', 'domain users']
        if v.lower() in reserved:
            raise ValueError(f'Group name {v} is reserved')
        return v


class GroupUpdate(BaseModel):
    """Schema for updating a group"""
    description: Optional[str] = Field(None, max_length=255)
    admin_password: str = Field(..., min_length=1)


class GroupMemberOperation(BaseModel):
    """Schema for adding/removing group members"""
    username: str = Field(..., min_length=1, max_length=64)


class GroupResponse(GroupBase):
    """Group response schema"""
    pass


class GroupListResponse(BaseModel):
    """Response for group list"""
    groups: List[GroupResponse]
    total: int
