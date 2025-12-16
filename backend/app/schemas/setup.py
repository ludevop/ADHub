from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class DNSBackendType(str, Enum):
    """DNS backend types"""
    SAMBA_INTERNAL = "SAMBA_INTERNAL"
    BIND9_DLZ = "BIND9_DLZ"
    NONE = "NONE"


class DomainFunctionLevel(str, Enum):
    """
    Domain functional levels supported by Samba 4.x
    Valid options: 2000, 2003, 2008, 2008_R2
    Note: 2008 is recommended for maximum compatibility
    """
    LEVEL_2000 = "2000"
    LEVEL_2003 = "2003"
    LEVEL_2008 = "2008"
    LEVEL_2008_R2 = "2008_R2"


class DomainConfigSchema(BaseModel):
    """Domain configuration for Samba AD DC provisioning"""

    # Domain settings
    realm: str = Field(..., description="Kerberos realm (e.g., EXAMPLE.COM)", min_length=3)
    domain: str = Field(..., description="NetBIOS domain name (e.g., EXAMPLE)", min_length=1, max_length=15)
    domain_name: str = Field(..., description="DNS domain name (e.g., example.com)", min_length=3)

    # Administrator settings
    admin_password: str = Field(..., description="Administrator password", min_length=8)

    # DNS settings
    dns_backend: DNSBackendType = Field(default=DNSBackendType.SAMBA_INTERNAL, description="DNS backend type")
    dns_forwarder: Optional[str] = Field(default="8.8.8.8", description="DNS forwarder IP address")

    # Server settings
    server_role: str = Field(default="dc", description="Server role")
    host_ip: Optional[str] = Field(default=None, description="Host IP address")

    # Functional level
    function_level: DomainFunctionLevel = Field(
        default=DomainFunctionLevel.LEVEL_2008,
        description="Domain functional level"
    )

    @validator('realm')
    def realm_must_be_uppercase(cls, v):
        """Realm should be uppercase"""
        if v != v.upper():
            raise ValueError('Realm must be uppercase (e.g., EXAMPLE.COM)')
        return v

    @validator('domain')
    def domain_must_be_uppercase_alphanumeric(cls, v):
        """NetBIOS domain must be uppercase and alphanumeric"""
        if not v.isalnum():
            raise ValueError('NetBIOS domain must be alphanumeric')
        if v != v.upper():
            raise ValueError('NetBIOS domain must be uppercase')
        return v

    @validator('domain_name')
    def domain_name_must_be_lowercase(cls, v):
        """DNS domain should be lowercase"""
        if v != v.lower():
            raise ValueError('DNS domain name should be lowercase (e.g., example.com)')
        if not all(c.isalnum() or c in '.-' for c in v):
            raise ValueError('DNS domain name contains invalid characters')
        return v

    @validator('admin_password')
    def validate_password_strength(cls, v):
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(not c.isalnum() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain uppercase, lowercase, and numbers')

        return v


class PrerequisiteCheck(BaseModel):
    """Prerequisites check result"""
    check_name: str
    status: str  # "passed", "failed", "warning"
    message: str
    details: Optional[str] = None


class PrerequisitesResponse(BaseModel):
    """Response for prerequisites check"""
    all_passed: bool
    checks: List[PrerequisiteCheck]


class ProvisionStatus(str, Enum):
    """Provision status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ProvisionResponse(BaseModel):
    """Response for provision request"""
    status: ProvisionStatus
    message: str
    task_id: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None


class VerificationTest(BaseModel):
    """Single verification test result"""
    test_name: str
    category: str  # "dns", "kerberos", "ldap", "services", "auth"
    status: str  # "passed", "failed", "skipped", "running"
    message: str
    details: Optional[str] = None
    duration_ms: Optional[int] = None


class VerificationResponse(BaseModel):
    """Response for verification tests"""
    overall_status: str  # "passed", "failed", "partial"
    total_tests: int
    passed: int
    failed: int
    skipped: int
    tests: List[VerificationTest]
    summary: str


class SetupStatusResponse(BaseModel):
    """Overall setup status"""
    is_provisioned: bool
    domain_info: Optional[dict] = None
    last_provision_date: Optional[str] = None
