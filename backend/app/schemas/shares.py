"""Share management schemas"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class ShareBase(BaseModel):
    """Base share schema"""
    name: str = Field(..., min_length=1, max_length=64)
    path: Optional[str] = None
    comment: Optional[str] = None
    read_only: bool = False
    guest_ok: bool = False
    browseable: bool = True


class ShareCreate(BaseModel):
    """Schema for creating a share"""
    name: str = Field(..., min_length=1, max_length=64, pattern=r'^[a-zA-Z0-9._-]+$')
    path: str = Field(..., min_length=1, max_length=255)
    comment: Optional[str] = Field(None, max_length=255)
    read_only: bool = False
    guest_ok: bool = False
    browseable: bool = True

    @field_validator('name')
    @classmethod
    def validate_sharename(cls, v):
        """Validate share name doesn't contain invalid characters"""
        if not v:
            raise ValueError('Share name cannot be empty')
        # Check for reserved names
        reserved = ['global', 'homes', 'printers', 'print$', 'ipc$']
        if v.lower() in reserved:
            raise ValueError(f'Share name {v} is reserved')
        return v

    @field_validator('path')
    @classmethod
    def validate_path(cls, v):
        """Validate path is not empty"""
        if not v or not v.strip():
            raise ValueError('Path cannot be empty')
        return v


class ShareUpdate(BaseModel):
    """Schema for updating a share"""
    path: Optional[str] = Field(None, min_length=1, max_length=255)
    comment: Optional[str] = Field(None, max_length=255)
    read_only: Optional[bool] = None
    guest_ok: Optional[bool] = None
    browseable: Optional[bool] = None


class ShareResponse(ShareBase):
    """Share response schema"""
    pass


class ShareListResponse(BaseModel):
    """Response for share list"""
    shares: List[ShareResponse]
    total: int
