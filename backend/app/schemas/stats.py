"""Statistics schemas"""

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_users: int
    total_groups: int
    total_shares: int
    total_dns_records: int
