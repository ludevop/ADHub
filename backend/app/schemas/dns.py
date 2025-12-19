"""DNS management schemas"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class DNSZone(BaseModel):
    """DNS Zone schema"""
    name: str
    type: str  # forward or reverse


class DNSRecord(BaseModel):
    """DNS Record schema"""
    zone: str
    name: str
    type: str  # A, AAAA, CNAME, MX, TXT, SRV, PTR, etc.
    data: str


class DNSRecordCreate(BaseModel):
    """Schema for creating a DNS record"""
    zone: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=10)
    data: str = Field(..., min_length=1, max_length=255)
    admin_password: str = Field(..., min_length=1)

    @field_validator('type')
    @classmethod
    def validate_record_type(cls, v):
        """Validate record type"""
        valid_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV', 'PTR', 'NS']
        if v.upper() not in valid_types:
            raise ValueError(f'Record type must be one of: {", ".join(valid_types)}')
        return v.upper()

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate record name"""
        if not v or not v.strip():
            raise ValueError('Record name cannot be empty')
        return v.strip()


class DNSRecordDelete(BaseModel):
    """Schema for deleting a DNS record"""
    zone: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=10)
    data: str = Field(..., min_length=1, max_length=255)
    admin_password: str = Field(..., min_length=1)

    @field_validator('type')
    @classmethod
    def validate_record_type(cls, v):
        """Validate record type"""
        return v.upper()


class DNSZoneListResponse(BaseModel):
    """Response for zone list"""
    zones: List[DNSZone]
    total: int


class DNSRecordListResponse(BaseModel):
    """Response for record list"""
    records: List[DNSRecord]
    total: int
    zone: str
